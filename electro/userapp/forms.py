from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    referral_code = forms.CharField(max_length=10, required=False, help_text="Enter a referral code if you have one.")

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)
