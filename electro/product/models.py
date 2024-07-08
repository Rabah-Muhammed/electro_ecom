from django.db import models
from category.models import Category
from django.contrib.auth.models import User
from django.db.models import Avg
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.urls import reverse


# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=200,unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    image1 = models.ImageField(upload_to='photos/products', blank=True, null=True)
    image2 = models.ImageField(upload_to='photos/products', blank=True, null=True)

    images_thumbnail = ImageSpecField(source='images',
                                      processors=[ResizeToFill(800, 800)],
                                      format='JPEG',
                                      options={'quality': 90})
    image1_thumbnail = ImageSpecField(source='image1',
                                      processors=[ResizeToFill(800, 800)],
                                      format='JPEG',
                                      options={'quality': 90})
    image2_thumbnail = ImageSpecField(source='image2',
                                      processors=[ResizeToFill(800, 800)],
                                      format='JPEG',
                                      options={'quality': 90})
    
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)


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