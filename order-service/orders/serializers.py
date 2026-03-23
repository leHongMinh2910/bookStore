from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderItem, Payment


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price_cart = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "customer_id", "status", "created_at", "items", "total_price_cart"]

    def get_total_price_cart(self, obj):
        return obj.cart_total


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
