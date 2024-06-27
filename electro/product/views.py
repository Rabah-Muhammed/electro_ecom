
from django.shortcuts import render,get_object_or_404
from category.models import Category
from . models import Product

# Create your views here.

def store(request,category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug) 
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()
    else:

        products = Product.objects.all().filter(is_available=True).order_by('-created_date')
        product_count = products.count()

    context = {
        'products':products,
        'product_count':product_count,
    }

    return render(request, 'layouts/products.html',context)


def product_detail(request,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        related_products = Product.objects.filter(category__slug=category_slug).exclude(slug=product_slug)
    except Exception as e:
        raise e
    
    context = {
        'single_product' : single_product,
        'products':related_products
    }

    return render(request,'layouts/product-detail.html',context)
