
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render,get_object_or_404
from category.models import Category
from .forms import ReviewForm
from product.models import Product, ReviewRatingz
from django.contrib import messages
from carts.views import _cart_id
from carts.models import CartItem
from django.db.models import Avg


# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None

    # Get all products or filter by category
    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('-created_date')
    else:
        products = Product.objects.all().filter(is_available=True).order_by('-created_date')

    # Calculate average rating for each product
    for product in products:
        product.avg_rating = product.averageReview()

    sort_option = request.GET.get('sort')
    if sort_option:
        if sort_option == 'price_low':
            products = products.order_by('price')
        elif sort_option == 'price_high':
            products = products.order_by('-price')

    # Filter by featured products
    featured_products = request.GET.get('featured')
    if featured_products:
        products = products.filter(is_featured=True)

    # Filter by rating
    filter_by_rating = request.GET.get('rating')
    if filter_by_rating:
        if filter_by_rating == '4plus':
            products = products.annotate(avg_rating=Avg('reviewratingz__rating')).filter(avg_rating__gte=4)
        elif filter_by_rating == '3plus':
            products = products.annotate(avg_rating=Avg('reviewratingz__rating')).filter(avg_rating__gte=3)
        elif filter_by_rating == '2plus':
            products = products.annotate(avg_rating=Avg('reviewratingz__rating')).filter(avg_rating__gte=2)
        elif filter_by_rating == '1plus':
            products = products.annotate(avg_rating=Avg('reviewratingz__rating')).filter(avg_rating__gte=1)

    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    paginated_products = paginator.get_page(page_number)

    context = {
        'products': paginated_products,
        'product_count': products.count(),
        'sort_option': sort_option,
    }

    return render(request, 'layouts/products.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
        related_products = Product.objects.filter(category__slug=category_slug).exclude(slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
    except Exception as e:
        raise e

    # get the reviews
    reviews = ReviewRatingz.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'related_products': related_products,
        'reviews': reviews,
        'in_cart': in_cart,
        
    }
    return render(request, 'layouts/product-detail.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
        related_products = Product.objects.filter(category__slug=category_slug).exclude(slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
    except Exception as e:
        raise e

    # get the reviews
    reviews = ReviewRatingz.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'related_products': related_products,
        'reviews': reviews,
        'in_cart': in_cart,
        
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