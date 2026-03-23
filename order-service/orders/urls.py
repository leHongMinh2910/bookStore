from django.urls import path

from .views import (
    AllOrdersView,
    CartDetailView,
    CartItemCreateView,
    CartItemDeleteView,
    CreateOrderView,
    CustomerOrdersView,
    PublisherOrdersView,
    update_order_status,
)

urlpatterns = [
    path("carts/<int:customer_id>/", CartDetailView.as_view(), name="cart-detail"),
    path("carts/<int:customer_id>/items/", CartItemCreateView.as_view(), name="cart-item-create"),
    path("carts/<int:customer_id>/items/<int:item_id>/", CartItemDeleteView.as_view(), name="cart-item-delete"),
    path("orders/", AllOrdersView.as_view(), name="all-orders"),
    path("orders/<int:customer_id>/create/", CreateOrderView.as_view(), name="order-create"),
    path("orders/customer/<int:customer_id>/", CustomerOrdersView.as_view(), name="customer-orders"),
    path("orders/publisher/<int:publisher_id>/", PublisherOrdersView.as_view(), name="publisher-orders"),
    path("orders/<int:pk>/status/", update_order_status, name="order-update-status"),
]
