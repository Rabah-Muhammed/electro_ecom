from django.urls import path
from . import views

urlpatterns = [
    path('alogin/', views.adminlogin, name='alogin'),
    path('ahome/', views.ahome, name='ahome'),
    path('alogout/', views.adminlogout, name='alogout'),
    path('userlist/', views.userlist, name='userlist'),
    path('user/block/<int:user_id>/', views.blockuser, name='blockuser'),
    path('user/unblock/<int:user_id>/', views.unblockuser, name='unblockuser'),
]
