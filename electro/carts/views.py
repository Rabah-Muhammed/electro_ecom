from datetime import datetime, time, timedelta
from decimal import Decimal
import json
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from carts.forms import CouponForm
from .models import Cart, CartItem, Coupon, Order, OrderItem, Payment, Wallet
from accounts.models import UserProfile,Address
from accounts.forms import AddressForm
from product.models import Product
from django.contrib.auth.decorators import login_required
from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.db import transaction
from django.urls import reverse


logger = logging.getLogger(__name__)

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


def cart(request):
    total = 0
    quantity = 0
    cart_items = None
    coupon = None
    discount = 0
    available_coupons = []

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.Quantity)
            quantity += cart_item.Quantity

        if cart.coupon:
            coupon = cart.coupon
            if coupon.is_valid() and total >= coupon.minimum_amount:
                discount = coupon.discount
                total -= discount

        # Get available coupons based on the total amount
        available_coupons = Coupon.objects.filter(
            active=True,
            expiry_date__gte=datetime.now().date(),
            minimum_amount__lte=total
        )

    except Cart.DoesNotExist:
        pass

    tax = (2 * total) / 100
    grand_total = total + tax

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'coupon': coupon,
        'discount': discount,
        'tax': tax,
        'grand_total': grand_total,
        'available_coupons': available_coupons,
    }

    return render(request, 'layouts/cart.html', context)

def fetch_coupons(request):
    total = float(request.GET.get('total', 0))
    available_coupons = Coupon.objects.filter(
        active=True,
        expiry_date__gte=datetime.now().date(),
        minimum_amount__lte=total
    ).values('code', 'discount')  # Fetch only the necessary fields

    coupons = list(available_coupons)
    return JsonResponse({'coupons': coupons})


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0 
    grand_total = 0 
    discount = 0
    delivery_charge = 50

    # Check if there is an order ID for repayment
    repay_order_id = request.session.get('repay_order_id')

    if repay_order_id:
        # Fetch the specific failed order for repayment
        order = get_object_or_404(Order, id=repay_order_id, status='Payment Failed')
        
        # Clear the session after retrieving the order
        del request.session['repay_order_id']

        # Use the order details to populate the checkout page
        cart_items = order.orderitem_set.all()  # Assuming the related name is `orderitem_set`
        total = order.total_amount
        discount = order.discount_amount
        grand_total = total + (2 * total / 100) + delivery_charge

    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.Quantity)
                quantity += cart_item.Quantity
            
            # Apply discount if a valid coupon is present
            if cart.coupon and cart.coupon.is_valid() and total >= cart.coupon.minimum_amount:
                discount = cart.coupon.discount
                total -= discount

            tax = (2 * total) / 100
            grand_total = total + tax + delivery_charge

            # Clear discount from session after applying
            if 'discount' in request.session:
                del request.session['discount']
        except Cart.DoesNotExist:
            cart_items = None

    try:
        user_profile = request.user.userprofile  # Assuming a OneToOne relationship
        addresses = Address.objects.filter(user_profile=user_profile)
    except UserProfile.DoesNotExist:
        addresses = None

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'addresses': addresses,
        'discount': discount,
        'delivery_charge': delivery_charge,  
    }
    return render(request, 'layouts/checkout.html', context)


def checkoutaddress(request):
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        address_form = AddressForm(request.POST)

        if address_form.is_valid():
            if address_id:  # Update existing address
                address = get_object_or_404(Address, id=address_id)
                form = AddressForm(request.POST, instance=address)
                form.save()
            else:  # Add new address
                new_address = address_form.save(commit=False)
                user_profile = UserProfile.objects.get(user=request.user)
                new_address.user_profile = user_profile
                new_address.save()

            return redirect('checkout')

    else:
        address_form = AddressForm()

    return render(request, 'checkout.html', {'address_form': address_form})



def editing_address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            # Redirect or show success message
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'checkout.html', {'address_form': form, 'address': address})

def deleting_address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
    return redirect('checkout')

@transaction.atomic
@login_required(login_url='login')
def place_order(request):
    if request.method == 'POST':
        address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method')

        try:
            # Get the selected address
            selected_address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            messages.error(request, 'The selected address does not exist.')
            return redirect('checkout')

        # Get the cart for the current user
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('checkout')

        # Calculate the total amount
        total_amount = sum(item.product.price * item.Quantity for item in cart_items)
        
        # Apply discount if a valid coupon is present
        discount = 0
        if cart.coupon and cart.coupon.is_valid() and total_amount >= cart.coupon.minimum_amount:
            discount = cart.coupon.discount
            total_amount -= discount

        deleting_charge = 50
        tax = (2 * total_amount) / 100
        grand_total = total_amount + tax + deleting_charge

        # Create an order with the delivery address
        order = Order.objects.create(
            user=request.user,
            total_amount=grand_total,
            coupon_amount=discount,
            status='Pending',
            delivery_address=f"{selected_address.address_line_1}, {selected_address.city}, {selected_address.state}"  # Format the address
        )

        # Create order items and decrease product quantity
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.Quantity
            )
            # Decrease the product quantity based on order quantity
            if cart_item.product.stock >= cart_item.Quantity:  # Check if there's enough stock
                cart_item.product.stock -= cart_item.Quantity
                cart_item.product.save()  # Save the updated product stock
            else:
                # Handle case where not enough stock is available (optional)
                messages.warning(request, f"Not enough stock for {cart_item.product.product_name}. Order may be adjusted.")

        # Clear the cart after placing the order
        cart_items.delete()

        messages.success(request, "Order placed successfully.")
        return redirect('order_placed', order.id)  # Redirect to order placed confirmation

    # Fetch addresses for the logged-in user
    user_profile = UserProfile.objects.get(user=request.user)
    user_addresses = Address.objects.filter(user_profile=user_profile)

    context = {
        'addresses': user_addresses,
    }

    return render(request, 'layouts/place_order.html', context)


@login_required(login_url='login')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Paginate orders
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'layouts/order_history.html', {'orders': page_obj})


def order_placed(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'layouts/order_placed.html', context)

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    
    total_amount = sum(item.product.price * item.quantity for item in order_items)
    tax = (2 * total_amount) / 100
    delivery_charge = 50
    grand_total = total_amount + tax + delivery_charge

    payment = Payment.objects.filter(order=order).first()

    # Calculate individual item totals
    item_totals = [
        {
            'product_name': item.product.product_name,
            'quantity': item.quantity,
            'price': item.product.price,
            'total': item.product.price * item.quantity
        }
        for item in order_items
    ]

    context = {
        'order': order,
        'item_totals': item_totals,
        'total_amount': total_amount,
        'tax': tax,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
        'payment_method': payment.payment_method if payment else 'Not Available'
    }
    return render(request, 'layouts/order_detail.html', context)



def view_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Calculate subtotals and additional details
    order_items = order.orderitem_set.all()
    for item in order_items:
        item.subtotal = item.product.price * item.quantity
    
    # Calculate grand total
    grand_total = order.total_amount - order.discount_amount - order.coupon_amount
    
    context = {
        'order': order,
        'payment_method': order.Payment.payment_method if order.Payment else 'COD',
        'order_items': order_items,
        'grand_total': grand_total
    }
    return render(request, 'layouts/invoice.html', context)

def invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Calculate subtotals and additional details
    order_items = order.orderitem_set.all()
    for item in order_items:
        item.subtotal = item.product.price * item.quantity

    # Calculate grand total
    grand_total = order.total_amount - order.discount_amount - order.coupon_amount
    
    context = {
        'order': order,
        'payment_method': order.Payment.payment_method if order.Payment else 'COD',
        'order_items': order_items,
        'grand_total': grand_total
    }
    
    html_string = render_to_string('layouts/invoice_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    HTML(string=html_string).write_pdf(response)
    return response

@csrf_exempt
@login_required(login_url='login')
def payments(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        payment_method = body.get('payment_method')
        payment_status = body.get('status')
        address_id = body.get('selected_address')
        
        try:
            selected_address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'The selected address does not exist.'})
        
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        if not cart_items.exists():
            return JsonResponse({'status': 'error', 'message': 'Your cart is empty.'})

        # Calculate the total amount
        total_amount = sum(item.product.price * item.Quantity for item in cart_items)
        
        discount = 0
        if cart.coupon and cart.coupon.is_valid() and total_amount >= cart.coupon.minimum_amount:
            discount = cart.coupon.discount
            total_amount -= discount

        delivery_charge = 50
        tax = (2 * total_amount) / 100
        grand_total = total_amount + tax + delivery_charge

        # Save payment information
        payment = Payment(
            user=request.user,
            payment_id=body.get('transID'),
            payment_method=payment_method,
            amount_paid=grand_total,
            status=payment_status,
        )
        payment.save()

        # Determine order status based on payment status
        order_status = 'Payment Failed' if payment_status == 'FAILED' else 'Pending'

        # Create the order with the delivery address
        order = Order.objects.create(
            user=request.user,
            Payment=payment,
            total_amount=grand_total,
            coupon_amount=discount,
            status=order_status,
            delivery_address=f"{selected_address.address_line_1}, {selected_address.city}, {selected_address.state}"  # Format the address
        )

        # Create order items and decrease product quantity
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                payment=payment,
                product=cart_item.product,
                quantity=cart_item.Quantity
            )
            # Decrease the product quantity based on order quantity
            if cart_item.product.stock >= cart_item.Quantity:
                cart_item.product.stock -= cart_item.Quantity
                cart_item.product.save()
        
        # Clear the cart if the payment was successful
        if payment_status != 'FAILED':
            cart_items.delete()

        return JsonResponse({'status': 'success', 'order_id': order.id})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def apply_coupon(request):
    coupon_code = request.GET.get('code')
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))
    
    try:
        coupon = Coupon.objects.get(code=coupon_code)
        if coupon.is_valid():
            total = sum(item.sub_total() for item in cart.cartitem_set.all())
            
            if total >= coupon.minimum_amount:
                cart.coupon = coupon
                cart.save()
                
                discount = coupon.discount
                total -= discount
                tax = (2 * total) / 100
                grand_total = total + tax
                
                # Save the discount in the session
                request.session['discount'] = discount
                
                response = {
                    'status': 'success',
                    'message': 'Coupon applied successfully.',
                    'total': total,
                    'discount': discount,
                    'tax': tax,
                    'grand_total': grand_total
                }
            else:
                response = {
                    'status': 'error',
                    'message': 'Cart total does not meet the minimum amount required for this coupon.'
                }
        else:
            response = {
                'status': 'error',
                'message': 'Invalid or expired coupon.'
            }
    except Coupon.DoesNotExist:
        response = {
            'status': 'error',
            'message': 'Coupon does not exist.'
        }
    
    return JsonResponse(response)

def remove_coupon(request):
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))
    
    if cart.coupon:
        cart.coupon = None
        cart.save()
        
        # Remove the discount from the session
        if 'discount' in request.session:
            del request.session['discount']

        total = sum(item.sub_total() for item in cart.cartitem_set.all())
        discount = 0
        tax = (2 * total) / 100
        grand_total = total + tax

        response = {
            'status': 'success',
            'message': 'Coupon removed successfully.',
            'total': total,
            'discount': discount,
            'tax': tax,
            'grand_total': grand_total
        }
    else:
        response = {
            'status': 'error',
            'message': 'No coupon applied to remove.'
        }
    
    return JsonResponse(response)

def manage_coupons(request):
    if request.method == 'POST':
        if 'create_coupon' in request.POST:
            form = CouponForm(request.POST)
            if form.is_valid():
                form.save()  # This will use the default value of active=True
                return redirect('manage_coupons')
        elif 'delete_coupon' in request.POST:
            coupon_id = request.POST.get('coupon_id')
            coupon = get_object_or_404(Coupon, id=coupon_id)
            coupon.delete()
            return JsonResponse({'status': 'success'})
    
    coupons = Coupon.objects.all()
    form = CouponForm()
    return render(request, 'manage_coupons.html', {'coupons': coupons, 'form': form})

@login_required(login_url='login')
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'Cancelled':
        messages.error(request, 'Order already cancelled.')
        return redirect('order_history')  # Change this to your actual order history view name
    
    try:
        # Increase the product quantity for each order item
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            item.product.stock += item.quantity  # Increase stock
            item.product.save()  # Save the updated product

        # Update the order status to cancelled
        order.status = 'Cancelled'
        order.save()

        # Convert total_amount to Decimal
        total_amount = Decimal(order.total_amount)
        
        # Update wallet balance
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += total_amount
        wallet.save()

        messages.success(request, 'Order cancelled and amount added to wallet.')
        logger.info(f"Order {order_id} cancelled successfully by user {request.user.id}. Amount {total_amount} added to wallet.")
    except Exception as e:
        messages.error(request, "There was an error cancelling the order. Please try again.")
        logger.error(f"Error cancelling order {order_id} by user {request.user.id}: {e}")

    return redirect('order_history')  # Change this to your actual order history view name



@login_required(login_url='login')
def wallet(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Retrieve cancelled orders for the logged-in user
    cancelled_orders = Order.objects.filter(user=request.user, status='Cancelled')
    
    # Retrieve order items for the cancelled orders and calculate the total amount
    cancelled_order_items = []
    for order in cancelled_orders:
        items = OrderItem.objects.filter(order=order)
        for item in items:
            item.total_price = item.product.price * item.quantity
            cancelled_order_items.append(item)
    
    context = {
        'wallet': wallet,
        'cancelled_order_items': cancelled_order_items,
    }
    
    return render(request, 'layouts/wallet.html', context)


@login_required(login_url='login')
def payment_failed(request):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    if not cart_items.exists():
        return redirect('cart')

    total_amount = sum(item.product.price * item.Quantity for item in cart_items)
    
    discount = 0
    if cart.coupon and cart.coupon.is_valid() and total_amount >= cart.coupon.minimum_amount:
        discount = cart.coupon.discount
        total_amount -= discount

    delivery_charge = 50
    tax = (2 * total_amount) / 100
    grand_total = total_amount + tax + delivery_charge

    # Get the selected address from the request (POST or query params)
    selected_address_id = request.POST.get('selected_address') or request.GET.get('selected_address')
    selected_address = None
    if selected_address_id:
        try:
            address_obj = Address.objects.get(id=selected_address_id)
            selected_address = f"{address_obj.address_line_1}, {address_obj.address_line_2}, {address_obj.city}, {address_obj.state}, {address_obj.country} - {address_obj.postal_code}"
        except Address.DoesNotExist:
            selected_address = "Address not found"

    payment_method = 'PayPal'  # Assuming PayPal was the method being used

    # Create order with Payment Failed status
    order = Order.objects.create(
        user=request.user,
        total_amount=grand_total,
        coupon_amount=discount,
        status='Payment Failed',
        delivery_address=selected_address,  # Use the correct field name
    )

    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.Quantity
        )

    return render(request, 'layouts/payment_failed.html', {'order': order})


@login_required(login_url='login')
def checkout_repay(request, order_id):
    order = get_object_or_404(Order, id=order_id, status='Payment Failed')

    # Get or create the cart
    cart_id = _cart_id(request)
    cart, created = Cart.objects.get_or_create(cart_id=cart_id)

    # Clear existing cart items
    CartItem.objects.filter(cart=cart).delete()

    # Add order items back to the cart
    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items:
        CartItem.objects.create(
            cart=cart,
            product=order_item.product,
            Quantity=order_item.quantity,  # Use Quantity instead of quantity
            is_active=True
        )
    
    return redirect('checkout')

