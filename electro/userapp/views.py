from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login,logout as logout_page
from django.contrib.auth.decorators import login_required
from product.models import Product

# Create your views here.
@login_required(login_url='login')
def index(request):
    products = Product.objects.all().filter(is_available=True)
    
    context = {
        'products':products,
    }
    return render(request,'layouts/index.html',context)


def register(request):
    if request.method=="POST":
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if pass1 != pass2:
            return render(request, 'layouts/register.html', {'error_message': 'Passwords do not match!!!'})
        
        elif User.objects.filter(username=uname).exists():
            return render(request, 'layouts/register.html', {'error_message': 'Username is already taken'})
        
        elif User.objects.filter(email=email).exists():
            return render(request, 'layouts/register.html', {'error_message': 'Email is already registered'})
        
        else:
            user=User.objects.create_user(uname,email,pass1)
            user.save()
            return render(request,'layouts/login.html')

    
    return render(request, 'layouts/register.html')


def login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)

        if user is not None:
            auth_login(request,user)
            return redirect('home')
        else:
             return render(request, 'layouts/login.html', {'error_message': 'You need to create account!!!'})
    return render(request,'layouts/login.html')

def logout(request):
    logout_page(request)
    return redirect('login')

