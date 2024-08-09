from django import forms
from accounts.models import Address, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext as _

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name')
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')
        widgets = {
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].required = False

class CustomPasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'New Password'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def clean_new_password1(self):

        password1 = self.cleaned_data.get('new_password1')
        
        if len(password1) < 8:
            raise forms.ValidationError(_('Password must be at least 8 characters long.'))

        if not any(char.isupper() for char in password1):
            raise forms.ValidationError(_('Password must contain at least one uppercase letter.'))

        if not any(char.isdigit() for char in password1):
            raise forms.ValidationError(_('Password must contain at least one digit.'))

        return password1
    

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'country', 'postal_code']


        