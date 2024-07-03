from django import forms
from product.models import ReviewRatingz,Product

class ReviewForm(forms.ModelForm):
    
    class Meta:
        model = ReviewRatingz
        fields = ['subject','review','rating']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'description', 'price', 'images', 'image1', 'image2', 'stock', 'is_available', 'category']


