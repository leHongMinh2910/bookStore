from decimal import Decimal

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem, Order, OrderItem, Payment
from .serializers import CartSerializer, OrderSerializer
from .service_clients import get_book, get_user, reserve_book


class CartDetailView(APIView):
    def get(self, request, customer_id):
        cart, _ = Cart.objects.get_or_create(customer_id=customer_id, status="InProgress")
        return Response({"cart": CartSerializer(cart).data})


class CartItemCreateView(APIView):
    def post(self, request, customer_id):
        customer, customer_error = get_user(customer_id)
        if customer_error:
            return Response({"detail": "Customer service lookup failed.", "error": customer_error}, status=status.HTTP_502_BAD_GATEWAY)

        cart, _ = Cart.objects.get_or_create(customer_id=customer_id, status="InProgress")
        book_id = request.data.get("book_id")
        quantity = int(request.data.get("quantity", 1))
        book, book_error = get_book(book_id)
        if book_error:
            return Response({"detail": "Catalog service lookup failed.", "error": book_error}, status=status.HTTP_502_BAD_GATEWAY)
        if quantity > int(book["total_number_of_book"]):
            return Response({"detail": "Quantity exceeds available stock."}, status=status.HTTP_400_BAD_REQUEST)

        item, _ = CartItem.objects.get_or_create(
            cart=cart,
            book_id=book["id"],
            defaults={
                "book_name": book["name"],
                "publisher_id": book["publisher_id"],
                "price": Decimal(str(book["price"])),
            },
        )
        item.book_name = book["name"]
        item.publisher_id = book["publisher_id"]
        item.price = Decimal(str(book["price"]))
        item.quantity = quantity
        item.total = float(item.price) * quantity
        item.save()

        return Response(
            {
                "msg": f"Book added successfully for {customer.get('first_name', '')}".strip(),
                "cart": CartSerializer(cart).data,
            },
            status=status.HTTP_200_OK,
        )


class CartItemDeleteView(APIView):
    def delete(self, request, customer_id, item_id):
        cart = Cart.objects.get(customer_id=customer_id, status="InProgress")
        item = CartItem.objects.get(cart=cart, pk=item_id)
        item.delete()
        return Response({"msg": "Book deleted successfully", "cart": CartSerializer(cart).data})


class CreateOrderView(APIView):
    def post(self, request, customer_id):
        customer, customer_error = get_user(customer_id)
        if customer_error:
            return Response({"detail": "Customer service lookup failed.", "error": customer_error}, status=status.HTTP_502_BAD_GATEWAY)

        cart = Cart.objects.filter(customer_id=customer_id, status="InProgress").first()
        if not cart or not cart.items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            customer_id=customer_id,
            total=cart.cart_total,
            delivery_country=request.data.get("country", "Unknown"),
            delivery_city=request.data.get("city", "Unknown"),
            delivery_street=request.data.get("street", "Unknown"),
            delivery_phone=request.data.get("phone", "Unknown"),
        )

        reserved_items = []
        for item in cart.items.all():
            _, reserve_error = reserve_book(item.book_id, item.quantity)
            if reserve_error:
                order.delete()
                return Response({"detail": "Could not reserve stock.", "error": reserve_error}, status=status.HTTP_502_BAD_GATEWAY)

            reserved_items.append(item.pk)
            OrderItem.objects.create(
                order=order,
                book_id=item.book_id,
                book_name=item.book_name,
                publisher_id=item.publisher_id,
                price=item.price,
                quantity=item.quantity,
                total=item.total,
            )

        Payment.objects.create(
            order=order,
            provider=request.data.get("provider", "demo-card"),
            card_last4=str(request.data.get("card_number", "4242424242424242"))[-4:],
            is_paid=True,
        )

        cart.status = "Completed"
        cart.save(update_fields=["status"])
        order.total = sum(order_item.total for order_item in order.items.all())
        order.save(update_fields=["total"])
        return Response(
            {
                "msg": f"Order created successfully for {customer.get('first_name', '')}".strip(),
                "order": OrderSerializer(order).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomerOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(customer_id=self.kwargs["customer_id"]).order_by("-ordered_date")


class PublisherOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(items__publisher_id=self.kwargs["publisher_id"]).distinct().order_by("-ordered_date")


class AllOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by("-ordered_date")


@api_view(["PATCH"])
def update_order_status(request, pk):
    order = Order.objects.get(pk=pk)
    order.status = request.data.get("status", order.status)
    order.save(update_fields=["status"])
    return Response({"order": OrderSerializer(order).data})
