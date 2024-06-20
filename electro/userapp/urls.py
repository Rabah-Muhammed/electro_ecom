
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('register/', views.register, name="register"),
    path('verify_otp/', views.verify_otp, name="verify_otp"),
    path('resend_otp/', views.resend_otp, name="resend_otp"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
]
