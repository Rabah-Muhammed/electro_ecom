
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',views.dashboard,name='dashboard'),
    path('orders/',views.orders,name='orders'),
    path('paymentmethod/',views.paymentmethod,name='paymentmethod'),
    path('profile/',views.profile,name='profile'),
    path('editprofile/',views.editprofile,name='editprofile'),
    path('change-password',views.change_password,name='change-password'),
    path('profile/add_address/', views.add_address, name='add_address'),
    path('profile/edit_address/<int:pk>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:pk>/', views.delete_address, name='delete_address'),
    
]

