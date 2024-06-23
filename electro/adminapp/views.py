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
from product.models import Product


logger = logging.getLogger(__name__)

def adminlogin(request):
    error_message = None 
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

@login_required(login_url='alogin')
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

def productlist(request):
    products = Product.objects.all()
    return render(request, 'productlist.html', {'products': products})

def addproduct(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        is_available = request.POST.get('is_available', False)
        
        # Ensure category exists
        category = get_object_or_404(Category, id=category_id)
        
        Product.objects.create(
            product_name=product_name,
            description=description,
            price=price,
            images=image,
            stock=stock,
            category=category,
            is_available=is_available
        )
        messages.success(request, 'Product added successfully.')
        return redirect('productlist')
    
    return render(request, 'addproduct.html')

def editproduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.category_id = request.POST.get('category')
        
        # Handling is_available checkbox
        is_available = request.POST.get('is_available', False)
        if is_available == 'on':
            product.is_available = True
        else:
            product.is_available = False
        
        image = request.FILES.get('image')
        if image:
            product.images = image
        
        try:
            
            product.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('productlist')
        except ValueError as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    categories = Category.objects.all()  # Fetch all categories for dropdown
    return render(request, 'editproduct.html', {'product': product, 'categories': categories})

def deleteproduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.is_deleted = True
        product.save()
        messages.success(request, f'Product "{product.product_name}" has been marked as deleted.')
        return redirect('productlist')
    
    return render(request, 'deleteproduct.html', {'product': product})