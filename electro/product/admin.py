from django.contrib import admin
from .models import Product, ReviewRatingz

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    fields = ('product_name', 'slug', 'description', 'price', 'images', 'image1', 'image2', 'stock', 'is_available', 'category')

admin.site.register(Product, ProductAdmin)
admin.site.register(ReviewRatingz)



