from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField()
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

class SubCategory(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField()
    parent = models.ForeignKey(Category, on_delete=models.CASCADE)
    details = models.TextField()
    color = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, default=0)
    stock = models.IntegerField()


class Favorite(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='favorited_by')
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        unique_together = ('user', 'product')


class CartItem(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')


class Order(models.Model):
    PAYMENT_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('kpay', 'KPay Screenshot'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='orders')
    total = models.FloatField(default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    kpay_screenshot = models.ImageField(blank=True, null=True, upload_to='kpay/')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    delivery_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(default=0)
