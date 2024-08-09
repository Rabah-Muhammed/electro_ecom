from django import forms

from product.models import Brand

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        label='End Date'
    )

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'slug', 'description']