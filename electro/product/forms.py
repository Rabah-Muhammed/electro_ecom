from django import forms
from product.models import Brand, ReviewRatingz,Product


class ReviewForm(forms.ModelForm):
    
    class Meta:
        model = ReviewRatingz
        fields = ['subject','review','rating']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'description', 'price', 'images', 'stock', 'is_available', 'category', 'is_deleted', 'is_featured','offer_percentage','brand']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


