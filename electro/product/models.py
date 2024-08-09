from datetime import timezone
from django.db import models
from category.models import Category
from django.contrib.auth.models import User
from django.db.models import Avg
from django.urls import reverse
from django.utils import timezone

# Create your models here.
class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True,null=True)
    slug = models.SlugField(max_length=200, unique=True,null=True)
    description = models.TextField(max_length=500, blank=True,null=True)

    def get_url(self):
        return reverse('brand_detail', args=[self.slug])

    def __str__(self):
        return self.name

class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=200,unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.IntegerField()
    offer_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    original_price = models.IntegerField(null=True, blank=True)
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True) 

    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])

    def __str__(self):
        return self.product_name
    
    def averageReview(self):
        reviews = ReviewRatingz.objects.filter(product=self,status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def get_discounted_price(self):
        highest_offer = self.offer_percentage if self.offer_percentage else 0
        category_offer = self.category.offer_percentage if self.category.offer_percentage else 0
        final_offer = max(highest_offer, category_offer)
        if final_offer:
            discounted_price = self.original_price * (1 - final_offer / 100)
            return round(discounted_price, 2)
        return self.original_price

    def save(self, *args, **kwargs):
        if self.original_price is None:
            self.original_price = self.price
        self.price = self.get_discounted_price()
        super(Product, self).save(*args, **kwargs)
    

class ProductGallery(models.Model):
    product = models.ForeignKey(Product,default=None,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/products',max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product_gallery'



class ReviewRatingz(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    subject = models.CharField(max_length=100,blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20,blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicates

    def __str__(self):
        return f"{self.user.username}'s Wishlist: {self.product.product_name}"