from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from carts.models import Cart, CartItem
from product.models import Product


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))
    
    cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart)
    if cart_item.Quantity < product.stock:
        cart_item.Quantity += 1
        cart_item.save()
        response_data = {'Quantity': cart_item.Quantity, 'sub_total': cart_item.sub_total()}
    else:
        response_data = {'error': 'Stock limit reached', 'Quantity': cart_item.Quantity}
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(response_data)
    
    return redirect('cart')

def remove_cart(request, product_id):
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.Quantity > 1:
            cart_item.Quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        
        response_data = {
            'Quantity': cart_item.Quantity if cart_item.Quantity > 0 else 0,
            'sub_total': cart_item.sub_total() if cart_item.Quantity > 0 else 0
        }
    except CartItem.DoesNotExist:
        response_data = {'Quantity': 0, 'sub_total': 0}
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(response_data)
    
    return redirect('cart')

def remove_cart_item(request, product_id):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.delete()
        return JsonResponse({'status': 'success'})
    except (Cart.DoesNotExist, Product.DoesNotExist, CartItem.DoesNotExist) as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def cart(request, total=0, Quantity=0, cart_items=None):
    tax = 0 
    grand_total = 0 

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.Quantity)
            Quantity += cart_item.Quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        cart_items = None

    context = {
        'total': total,
        'Quantity': Quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'layouts/cart.html', context)
