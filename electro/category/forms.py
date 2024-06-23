# category/forms.py

from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'slug', 'description', 'cat_image','is_deleted']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally customize form fields or widgets here
