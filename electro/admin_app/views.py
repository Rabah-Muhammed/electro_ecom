from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import logging
from django.shortcuts import render
from django.contrib.auth.models import User 
from .models import Profile

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
        # Optionally: You can add a success message or redirect to a different page.
    return redirect('userlist')
