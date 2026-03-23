from django.db import models


class Cart(models.Model):
    STATUS_CHOICES = (
        ("InProgress", "InProgress"),
        ("Completed", "Completed"),
    )

    customer_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="InProgress")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def cart_total(self):
        return round(sum(item.total for item in self.items.all()), 2)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book_id = models.IntegerField()
    book_name = models.CharField(max_length=255)
    publisher_id = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    total = models.FloatField(default=0)


class Order(models.Model):
    STATUS_CHOICES = (
        ("Received", "Received"),
        ("Processed", "Processed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
    )

    customer_id = models.IntegerField()
    ordered_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Received")
    total = models.FloatField(default=0)
    delivery_country = models.CharField(max_length=100)
    delivery_city = models.CharField(max_length=100)
    delivery_street = models.CharField(max_length=255)
    delivery_phone = models.CharField(max_length=20)
    is_ordered = models.BooleanField(default=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book_id = models.IntegerField()
    book_name = models.CharField(max_length=255)
    publisher_id = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    total = models.FloatField(default=0)


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    provider = models.CharField(max_length=50, default="demo-card")
    card_last4 = models.CharField(max_length=4)
    is_paid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
