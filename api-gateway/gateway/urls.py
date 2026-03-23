from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("books/<int:book_id>/add-to-cart/", views.add_to_cart, name="add-to-cart"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/items/<int:item_id>/delete/", views.delete_cart_item, name="delete-cart-item"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("dashboard/admin/", views.admin_dashboard, name="admin-dashboard"),
    path("dashboard/publisher/", views.publisher_dashboard, name="publisher-dashboard"),
    path("dashboard/publisher/category/new/", views.create_category, name="create-category"),
    path("dashboard/publisher/author/new/", views.create_author, name="create-author"),
    path("dashboard/publisher/book/new/", views.create_book, name="create-book"),
    path("orders/", views.orders_view, name="orders"),
]
