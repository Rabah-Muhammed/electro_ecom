from django.urls import path
from . import views

urlpatterns = [
    path('alogin/', views.adminlogin, name='alogin'),
    path('ahome/', views.ahome, name='ahome'),
    path('alogout/', views.adminlogout, name='alogout'),
    path('userlist/', views.userlist, name='userlist'),
    path('user/block/<int:user_id>/', views.blockuser, name='blockuser'),
    path('user/unblock/<int:user_id>/', views.unblockuser, name='unblockuser'),
    path('categories/',views.categorylist,name='categorylist'),
    path('category/add/', views.addcategory, name='addcategory'),
    path('category/edit/<int:category_id>/', views.editcategory, name='editcategory'),
    path('category/delete/<int:category_id>/', views.deletecategory, {'soft_delete': True}, name='deletecategory'),
    path('category/hard_delete/<int:category_id>/', views.deletecategory, {'soft_delete': False}, name='hard_deletecategory'),

]