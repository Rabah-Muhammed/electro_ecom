from datetime import datetime
from accounts.models import Address
from django.db import models
from django.contrib.auth.models import User
from product.models import Product

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.FloatField(help_text="Percentage discount for this coupon")
    active = models.BooleanField(default=True)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Minimum cart amount required to use this coupon")
    expiry_date = models.DateField(help_text="The date when the coupon expires")

    def is_valid(self):
        return self.active and self.expiry_date >= datetime.now().date()

    def __str__(self):
        return self.code

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cart_id = models.CharField(max_length=250,blank=True)
    date_added = models.DateField(auto_now_add=True)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    Quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    

    def sub_total(self):
        return self.product.price * self.Quantity

    def __str__(self):
        return f'{self.Quantity} of {self.product.product_name}' 
    
class Payment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Payment =models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    product = models.ManyToManyField(Product, through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')  # e.g., Pending, Completed, Cancelled
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_address = models.CharField(max_length=255,null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
 

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    quantity = models.PositiveIntegerField()


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.username}'s Wallet"
    


    