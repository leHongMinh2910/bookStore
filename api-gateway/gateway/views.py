from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import AddToCartForm, AuthorForm, BookForm, CategoryForm, CheckoutForm, LoginForm, RegisterForm
from .service_clients import call_service, catalog_url, identity_url, order_url


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


def _get_token(request):
    return request.session.get("access_token")


def _get_user(request):
    return request.session.get("user")


def _is_admin(request):
    return bool(_get_user(request) and _get_user(request).get("is_admin"))


def _refresh_cart_count(request):
    user = _get_user(request)
    if not user:
        request.session["cart_count"] = 0
        return None
    cart, status_code = call_service("GET", order_url(f"/api/carts/{user['id']}/"), token=_get_token(request))
    if status_code == 200 and cart:
        items = cart.get("cart", {}).get("items", [])
        request.session["cart_count"] = len(items)
        return cart.get("cart")
    request.session["cart_count"] = 0
    return None


def home(request):
    books_payload, _ = call_service("GET", catalog_url("/api/books/"))
    best_rated_payload, _ = call_service("GET", catalog_url("/api/books/best-rated/"))
    return render(
        request,
        "gateway/home.html",
        {
            "books": books_payload or [],
            "best_rated": best_rated_payload or [],
            "add_to_cart_form": AddToCartForm(),
        },
    )


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if (
            form.cleaned_data["email"] == ADMIN_USERNAME
            and form.cleaned_data["password"] == ADMIN_PASSWORD
        ):
            request.session["access_token"] = ""
            request.session["refresh_token"] = ""
            request.session["user"] = {
                "id": 0,
                "email": ADMIN_USERNAME,
                "first_name": "Admin",
                "last_name": "Nha sach vui ve",
                "is_publisher": False,
                "is_admin": True,
            }
            request.session["cart_count"] = 0
            messages.success(request, "Dang nhap admin thanh cong.")
            return redirect("create-book")

        payload, status_code = call_service("POST", identity_url("/api/token/"), json=form.cleaned_data)
        if status_code == 200 and payload:
            user = {
                "email": payload.get("email"),
                "first_name": payload.get("first_name"),
                "last_name": payload.get("last_name"),
                "is_publisher": payload.get("is_publisher"),
                "is_admin": False,
            }
            me_payload, me_status = call_service("GET", identity_url("/api/me/"), token=payload.get("access"))
            if me_status == 200 and me_payload:
                user.update(me_payload)
            request.session["access_token"] = payload.get("access")
            request.session["refresh_token"] = payload.get("refresh")
            request.session["user"] = user
            _refresh_cart_count(request)
            messages.success(request, "JWT login successful.")
            return redirect("home")
        messages.error(request, (payload or {}).get("detail", "Login failed."))
    return render(request, "gateway/login.html", {"form": form})


def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data.copy()
        is_publisher = data.pop("is_publisher")
        endpoint = "/api/publishers/register/" if is_publisher else "/api/users/register/"
        if not is_publisher:
            data.pop("certificate", None)
        payload, status_code = call_service("POST", identity_url(endpoint), json=data)
        if status_code in (200, 201):
            messages.success(request, "Registration successful. Please log in.")
            return redirect("login")
        messages.error(request, str(payload))
    return render(request, "gateway/register.html", {"form": form})


def logout_view(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect("home")


def add_to_cart(request, book_id):
    user = _get_user(request)
    if not user:
        messages.warning(request, "Please log in before adding to cart.")
        return redirect("login")
    if request.method == "POST":
        form = AddToCartForm(request.POST)
        if form.is_valid():
            payload, status_code = call_service(
                "POST",
                order_url(f"/api/carts/{user['id']}/items/"),
                token=_get_token(request),
                json={"book_id": book_id, "quantity": form.cleaned_data["quantity"]},
            )
            if status_code == 200:
                _refresh_cart_count(request)
                messages.success(request, "Book added to cart.")
            else:
                messages.error(request, (payload or {}).get("detail", "Could not add book to cart."))
    return redirect("home")


def cart_view(request):
    user = _get_user(request)
    if not user:
        return redirect("login")
    cart = _refresh_cart_count(request) or {"items": [], "total_price_cart": 0}
    return render(request, "gateway/cart.html", {"cart": cart})


def delete_cart_item(request, item_id):
    user = _get_user(request)
    if not user:
        return redirect("login")
    if request.method == "POST":
        _, status_code = call_service(
            "DELETE",
            order_url(f"/api/carts/{user['id']}/items/{item_id}/"),
            token=_get_token(request),
        )
        if status_code in (200, 204):
            messages.success(request, "Cart item removed.")
        else:
            messages.error(request, "Could not remove cart item.")
        _refresh_cart_count(request)
    return redirect("cart")


def checkout_view(request):
    user = _get_user(request)
    if not user:
        return redirect("login")
    cart = _refresh_cart_count(request)
    if not cart or not cart.get("items"):
        messages.info(request, "Your cart is empty.")
        return redirect("home")
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        payload, status_code = call_service(
            "POST",
            order_url(f"/api/orders/{user['id']}/create/"),
            token=_get_token(request),
            json=form.cleaned_data,
        )
        if status_code == 201:
            request.session["cart_count"] = 0
            messages.success(request, "Order created successfully.")
            return redirect("orders")
        messages.error(request, str(payload))
    return render(request, "gateway/checkout.html", {"form": form, "cart": cart})


def orders_view(request):
    user = _get_user(request)
    if not user:
        return redirect("login")
    if user.get("is_admin"):
        payload, _ = call_service("GET", order_url("/api/orders/"), token=_get_token(request))
        return render(request, "gateway/orders.html", {"orders": payload or []})
    if user.get("is_publisher"):
        payload, _ = call_service("GET", order_url(f"/api/orders/publisher/{user['id']}/"), token=_get_token(request))
    else:
        payload, _ = call_service("GET", order_url(f"/api/orders/customer/{user['id']}/"), token=_get_token(request))
    return render(request, "gateway/orders.html", {"orders": payload or []})


def admin_dashboard(request):
    if not _is_admin(request):
        messages.warning(request, "Hay dang nhap bang admin/admin de vao trang nay.")
        return redirect("login")

    users_payload, _ = call_service("GET", identity_url("/api/users/"))
    publishers_payload, _ = call_service("GET", identity_url("/api/publishers/"))
    authors_payload, _ = call_service("GET", identity_url("/api/authors/"))
    categories_payload, _ = call_service("GET", catalog_url("/api/categories/"))
    books_payload, _ = call_service("GET", catalog_url("/api/books/"))
    orders_payload, _ = call_service("GET", order_url("/api/orders/"))

    return render(
        request,
        "gateway/admin_dashboard.html",
        {
            "stats": {
                "users": len(users_payload or []) + len(publishers_payload or []),
                "orders": len(orders_payload or []),
                "books": len(books_payload or []),
            },
            "books": books_payload or [],
            "authors": authors_payload or [],
            "categories": categories_payload or [],
            "orders": orders_payload or [],
        },
    )


def publisher_dashboard(request):
    user = _get_user(request)
    if not user or not user.get("is_publisher"):
        messages.warning(request, "Publisher account required.")
        return redirect("home")
    books_payload, _ = call_service("GET", catalog_url(f"/api/books/publisher/{user['id']}/"), token=_get_token(request))
    authors_payload, _ = call_service("GET", identity_url("/api/authors/"), token=_get_token(request))
    categories_payload, _ = call_service("GET", catalog_url("/api/categories/"), token=_get_token(request))
    return render(
        request,
        "gateway/publisher_dashboard.html",
        {
            "books": books_payload or [],
            "authors": [a for a in (authors_payload or []) if a.get("publisher") == user["id"]],
            "categories": categories_payload or [],
        },
    )


def create_category(request):
    user = _get_user(request)
    if not user or (not user.get("is_publisher") and not user.get("is_admin")):
        return redirect("home")
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        _, status_code = call_service("POST", catalog_url("/api/categories/"), token=_get_token(request), json=form.cleaned_data)
        if status_code in (200, 201):
            messages.success(request, "Category created.")
        else:
            messages.error(request, "Could not create category.")
        return redirect("admin-dashboard" if user.get("is_admin") else "publisher-dashboard")
    return render(request, "gateway/simple_form.html", {"title": "Them the loai", "form": form})


def create_author(request):
    user = _get_user(request)
    if not user or (not user.get("is_publisher") and not user.get("is_admin")):
        return redirect("home")
    publishers_payload, _ = call_service("GET", identity_url("/api/publishers/"))
    form = AuthorForm(request.POST or None)
    form.fields["publisher"].choices = [(str(item["id"]), f"{item['first_name']} {item['last_name']}") for item in (publishers_payload or [])]
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        if user.get("is_admin") and not data.get("publisher"):
            messages.error(request, "Admin can chon mot nha phat hanh cho tac gia.")
            return render(request, "gateway/simple_form.html", {"title": "Them tac gia", "form": form})
        data["publisher"] = int(data["publisher"] or user["id"])
        _, status_code = call_service("POST", identity_url("/api/authors/"), token=_get_token(request), json=data)
        if status_code in (200, 201):
            messages.success(request, "Author created.")
        else:
            messages.error(request, "Could not create author.")
        return redirect("admin-dashboard" if user.get("is_admin") else "publisher-dashboard")
    return render(request, "gateway/simple_form.html", {"title": "Them tac gia", "form": form})


def create_book(request):
    user = _get_user(request)
    if not user or (not user.get("is_publisher") and not user.get("is_admin")):
        return redirect("home")
    category_payload, _ = call_service("GET", catalog_url("/api/categories/"), token=_get_token(request))
    author_payload, _ = call_service("GET", identity_url("/api/authors/"), token=_get_token(request))
    publishers_payload, _ = call_service("GET", identity_url("/api/publishers/"), token=_get_token(request))
    form = BookForm(request.POST or None)
    form.fields["category"].choices = [(str(item["id"]), item["name"]) for item in (category_payload or [])]
    publisher_authors = author_payload or []
    if user.get("is_publisher") and not user.get("is_admin"):
        publisher_authors = [item for item in (author_payload or []) if item.get("publisher") == user["id"]]
    form.fields["author_id"].choices = [(str(item["id"]), f"{item['first_name']} {item['last_name']}") for item in publisher_authors]
    form.fields["publisher_id"].choices = [(str(item["id"]), f"{item['first_name']} {item['last_name']}") for item in (publishers_payload or [])]
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        if user.get("is_admin"):
            if not data.get("publisher_id"):
                messages.error(request, "Admin can chon mot nha phat hanh truoc khi them sach.")
                return render(request, "gateway/simple_form.html", {"title": "Them sach", "form": form})
            data["publisher_id"] = int(data["publisher_id"])
        else:
            data["publisher_id"] = user["id"]
        data["category"] = int(data["category"])
        data["author_id"] = int(data["author_id"])
        _, status_code = call_service("POST", catalog_url("/api/books/"), token=_get_token(request), json=data)
        if status_code in (200, 201):
            messages.success(request, "Book created.")
        else:
            messages.error(request, "Could not create book.")
        return redirect("admin-dashboard" if user.get("is_admin") else "publisher-dashboard")
    return render(request, "gateway/simple_form.html", {"title": "Them sach", "form": form})
