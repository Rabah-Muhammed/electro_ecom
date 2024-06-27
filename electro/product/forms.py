from django import forms
from product.models import ReviewRatingz

class ReviewForm(forms.ModelForm):
    
    class Meta:
        model = ReviewRatingz
        fields = ['subject','review','rating']