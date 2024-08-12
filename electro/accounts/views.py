from django.http import JsonResponse

from carts.models import Order
from .models import Address
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import AddressForm, CustomPasswordChangeForm, UserForm, UserProfileForm
from django.contrib.auth import update_session_auth_hash,logout
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.cache import cache_control
from .forms import AddressForm
from django.core.paginator import Paginator

def dashboard(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'dashboard.html', context)


def orders(request):
    order_list = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(order_list, 10)  # Show 10 orders per page

    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)

    return render(request, 'orders.html', {'orders': orders})

def paymentmethod(request):
    return render(request,'paymentm.html')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)  
def profile(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    addresses = user_profile.addresses.all()  # Retrieve all addresses associated with the user profile

    context = {
        'user': user,
        'user_profile': user_profile,
        'addresses': addresses,  # Include addresses in the context
    }
    return render(request, 'profile.html', context)


@cache_control(no_cache=True,must_revalidate=True,no_store=True)  
def editprofile(request):
    user = request.user
    userprofile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('editprofile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        initial_user_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        user_form = UserForm(instance=request.user, initial=initial_user_data)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'editprofile.html', context)

def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update session hash with new password
            messages.success(request, 'Your password was successfully updated!')
            return redirect('login')  # Redirect to login or another appropriate view
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

def add_address(request):
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            # Save the form data to create a new Address object
            new_address = address_form.save(commit=False)
            user_profile = UserProfile.objects.get(user=request.user)
            new_address.user_profile = user_profile
            new_address.save()
            return redirect('profile')  # Redirect to profile page after successful submission
    else:
        address_form = AddressForm()

    return render(request, 'addaddress.html', {'address_form': address_form})



def edit_address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            # Redirect or show success message
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'editaddress.html', {'address_form': form, 'address': address})

def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
    return redirect('profile')

