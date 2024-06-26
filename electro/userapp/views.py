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
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as logout_page
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from category.models import Category
from product.models import Product
from .models import OTP
from .forms import RegisterForm, OTPForm
from django.views.decorators.cache import never_cache
from django.views.decorators.cache import cache_control

from .models import User


def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_via_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


@cache_control(no_cache=True,must_revalidate=True,no_store=True)  
def index(request):
    
    category = Category.objects.get(category_name='Gaming') 
    products = Product.objects.filter(category=category, is_available=True)

    recent_arrivals_names = ['SKMEI Mens Watch New Wheels', 'CMF by Nothing Buds Pro', 'ZEBRONICS-Transformer-mouse', 'Apple iPhone 15 Pro Max']
    recent_arrivals = Product.objects.filter(product_name__in=recent_arrivals_names, is_available=True)

    context = {
        'products': products,
        'recent_arrivals':recent_arrivals
        }
    return render(request, 'layouts/index.html', context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)  
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
               
                user = User(username=uname, email=email, is_active=False)
                user.set_password(pass1)
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

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('register')

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            try:
                user_otp = OTP.objects.get(user=user, otp=otp)
                if user_otp.is_valid():
                    user.is_active = True
                    user.save()
                    user_otp.delete()
                    del request.session['user_id']
                    return redirect('login')
                else:
                    return render(request, 'layouts/verify_otp.html', {'form': form, 'error_message': 'OTP is expired or invalid'})
            except OTP.DoesNotExist:
                return render(request, 'layouts/verify_otp.html', {'form': form, 'error_message': 'OTP is expired or invalid'})
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


@cache_control(no_cache=True,must_revalidate=True,no_store=True)  
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect('home')
            else:
                # User is not active, show error message
                messages.error(request, 'Your account is not active. Please contact support.')
                return render(request, 'layouts/login.html')
        else:
            # Authentication failed, show error message
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, 'layouts/login.html')
    
    return render(request, 'layouts/login.html')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)  
def logout(request):
    logout_page(request)
    return redirect('/')

