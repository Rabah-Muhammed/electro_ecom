# from django.shortcuts import render,redirect
# from django.http import HttpResponse
# from django.contrib.auth.models import User,auth
# from django.contrib import messages
# from django.contrib.auth import authenticate,login as auth_login,logout as logout_page
# from django.contrib.auth.decorators import login_required
# from product.models import Product

# # Create your views here.
# @login_required(login_url='login')
# def index(request):
#     products = Product.objects.all().filter(is_available=True)
    
#     context = {
#         'products':products,
#     }
#     return render(request,'layouts/index.html',context)


# def register(request):
#     if request.method=="POST":
#         uname=request.POST.get('username')
#         email=request.POST.get('email')
#         pass1=request.POST.get('password1')
#         pass2=request.POST.get('password2')

#         if pass1 != pass2:
#             return render(request, 'layouts/register.html', {'error_message': 'Passwords do not match!!!'})
        
#         elif User.objects.filter(username=uname).exists():
#             return render(request, 'layouts/register.html', {'error_message': 'Username is already taken'})
        
#         elif User.objects.filter(email=email).exists():
#             return render(request, 'layouts/register.html', {'error_message': 'Email is already registered'})
        
#         else:
#             user=User.objects.create_user(uname,email,pass1)
#             user.save()
#             return render(request,'layouts/login.html')

    
#     return render(request, 'layouts/register.html')


# def login(request):
#     if request.method=='POST':
#         username=request.POST.get('username')
#         pass1=request.POST.get('pass')
#         user=authenticate(request,username=username,password=pass1)

#         if user is not None:
#             auth_login(request,user)
#             return redirect('home')
#         else:
#              return render(request, 'layouts/login.html', {'error_message': 'You need to create account!!!'})
#     return render(request,'layouts/login.html')

# def logout(request):
#     logout_page(request)
#     return redirect('login')

import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as logout_page
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from product.models import Product
from .models import OTP
from .forms import RegisterForm, OTPForm



def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_via_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

@login_required(login_url='login')
def index(request):
    products = Product.objects.all().filter(is_available=True)
    context = {'products': products}
    return render(request, 'layouts/index.html', context)

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data['username']
            email = form.cleaned_data['email']
            pass1 = form.cleaned_data['password1']
            pass2 = form.cleaned_data['password2']

            if pass1 != pass2:
                return render(request, 'layouts/register.html', {'form': form, 'error_message': 'Passwords do not match!!!'})

            elif User.objects.filter(username=uname).exists():
                return render(request, 'layouts/register.html', {'form': form, 'error_message': 'Username is already taken'})

            elif User.objects.filter(email=email).exists():
                return render(request, 'layouts/register.html', {'form': form, 'error_message': 'Email is already registered'})

            else:
                user = User(username=uname, email=email)
                user.set_password(pass1)
                user.is_active = False  # Deactivate account till it is confirmed
                user.save()

                otp = generate_otp()
                OTP.objects.create(user=user, otp=otp)
                send_otp_via_email(email, otp)

                request.session['user_id'] = user.id
                return redirect('verify_otp')

    else:
        form = RegisterForm()

    return render(request, 'layouts/register.html', {'form': form})

def verify_otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            try:
                user = User.objects.get(id=user_id)
                user_otp = OTP.objects.get(user=user, otp=otp)
                if user_otp.is_valid():
                    user.is_active = True
                    user.save()
                    user_otp.delete()
                    del request.session['user_id']
                    return redirect('login')
                else:
                    return render(request, 'layouts/verify_otp.html', {'form': form, 'error_message': 'OTP is expired'})
            except OTP.DoesNotExist:
                return render(request, 'layouts/verify_otp.html', {'form': form, 'error_message': 'Invalid OTP'})

    else:
        form = OTPForm()

    return render(request, 'layouts/verify_otp.html', {'form': form})

def resend_otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')

    user = User.objects.get(id=user_id)
    otp = generate_otp()
    OTP.objects.create(user=user, otp=otp)
    send_otp_via_email(user.email, otp)

    return redirect('verify_otp')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        user = authenticate(request, username=username, password=pass1)

        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'layouts/login.html', {'error_message': 'You need to create an account!!!'})
    return render(request, 'layouts/login.html')

def logout(request):
    logout_page(request)
    return redirect('login')

