from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import logging
from django.shortcuts import render
from django.contrib.auth.models import User 
from .models import Profile
from category.models import Category


logger = logging.getLogger(__name__)

def adminlogin(request):
    error_message = None  # Initialize the error_message variable
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        logger.debug(f"Username: {username}, Password: {password}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            logger.debug(f"Authenticated user: {user.username}, is_superuser: {user.is_superuser}")
        else:
            logger.debug("Authentication failed")

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('ahome')
        else:
            error_message = "Invalid credentials or not a superuser"
    
    return render(request, 'adminlogin.html', {'error_message': error_message})

@login_required
def ahome(request):
    return render(request, 'ahome.html')

def adminlogout(request):
    logout(request)
    return redirect('alogin')

def userlist(request):
    users = User.objects.all() 
    return render(request, 'userlist.html', {'users': users})

def blockuser(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        profile = Profile.objects.get_or_create(user=user)[0]
        profile.is_blocked = True
        profile.save()
       
    return redirect('userlist')

def unblockuser(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        profile = Profile.objects.get_or_create(user=user)[0]
        profile.is_blocked = False
        profile.save()
       
    return redirect('userlist')


def categorylist(request):
    categories = Category.objects.all()
    return render(request, 'categorylist.html', {'categories': categories})


def addcategory(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        cat_image = request.FILES.get('cat_image')
        
     
        if Category.objects.filter(category_name=category_name).exists():
            messages.error(request, f'A category with the name "{category_name}" already exists.')
            return render(request, 'categoryform.html')
        
        Category.objects.create(
            category_name=category_name,
            slug=slug,
            description=description,
            cat_image=cat_image
        )
        messages.success(request, 'Category added successfully.')
        return redirect('categorylist')
    
    return render(request, 'categoryform.html')

def editcategory(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        cat_image = request.FILES.get('cat_image')
        
        # Check if the updated category name already exists (excluding current category)
        if category_name != category.category_name and Category.objects.filter(category_name=category_name).exists():
            messages.error(request, f'A category with the name "{category_name}" already exists.')
            return render(request, 'categoryform.html', {'category': category})
        
        category.category_name = category_name
        category.slug = slug
        category.description = description
        if cat_image:
            category.cat_image = cat_image
        category.save()
        
        messages.success(request, 'Category updated successfully.')
        return redirect('categorylist')
    
    return render(request, 'categoryform.html', {'category': category})

def deletecategory(request, category_id, soft_delete=True):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        if soft_delete:
            category.is_deleted = True
            category.save()
            messages.success(request, f'Category "{category.category_name}" has been marked as deleted.')
        else:
            category.delete()
            messages.success(request, f'Category "{category.category_name}" has been deleted successfully.')
        
        return redirect('categorylist')
    
    return render(request, 'deletecategory.html', {'category': category})