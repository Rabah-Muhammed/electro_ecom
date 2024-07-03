
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render,get_object_or_404
from category.models import Category
from .forms import ReviewForm
from product.models import Product, ReviewRatingz
from django.contrib import messages


# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('-created_date')
    else:
        products = Product.objects.all().filter(is_available=True).order_by('-created_date')

    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    paginated_products = paginator.get_page(page_number)

    context = {
        'products': paginated_products,
        'product_count': products.count(),
    }

    return render(request, 'layouts/products.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
        related_products = Product.objects.filter(category__slug=category_slug).exclude(slug=product_slug)
      
    except Exception as e:
        raise e

    # get the reviews
    reviews = ReviewRatingz.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'related_products': related_products,
        'reviews': reviews,
        
    }
    return render(request, 'layouts/product-detail.html', context)



def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        try:
            reviews = ReviewRatingz.objects.get(user__id=request.user.id,product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRatingz.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRatingz()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)