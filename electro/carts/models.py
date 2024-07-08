from django.db import models
from django.contrib.auth.models import User
from product.models import Product

class Cart(models.Model):
    cart_id = models.CharField(max_length=250,blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    Quantity = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.Quantity

    def __str__(self):
        return self.product
    
    