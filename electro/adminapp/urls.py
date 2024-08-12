from django.urls import path
from . import views

urlpatterns = [
    path('alogin/', views.adminlogin, name='alogin'),
    path('ahome/', views.ahome, name='ahome'),
    path('alogout/', views.adminlogout, name='alogout'),
    path('userlist/',views.user_list,name='userlist'),
    path('update-status/<int:user_id>/', views.update_status, name='update_status'),
    path('categories/',views.categorylist,name='categorylist'),
    path('categories/add/', views.addcategory, name='addcategories'),
    path('categories/edit/<int:category_id>/', views.editcategory, name='editcategory'),
    path('categories/delete/<int:category_id>/', views.deletecategory, {'soft_delete': True}, name='deletecategory'),
    path('categories/hard_delete/<int:category_id>/', views.deletecategory, {'soft_delete': False}, name='hard_deletecategory'),
    path('productlist/',views.productlist,name='productlist'),
    path('product/add/', views.addproduct, name='addproduct'),
    path('product/edit/<int:product_id>/', views.editproduct, name='editproduct'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('brand-list/', views.brand_list, name='brand_list'),
    path('product/hard_delete/<int:product_id>/', views.delete_product, name='hard_delete_product'),
    path('delete-gallery-image/', views.delete_gallery_image, name='delete_gallery_image'),
    path('manage_orders/', views.manage_orders, name='manage_orders'),
    path('return_order/<int:order_id>/', views.return_order, name='return_order'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('top_selling/', views.top_selling_view, name='top_selling'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('ledger-book/', views.ledger_book, name='ledger_book'),
    path('product/<int:product_id>/delete_gallery_image/', views.delete_gallery_image, name='delete_gallery_image'),
    path('api/available_dates/', views.available_dates, name='available_dates'),
    path('api/get_available_order_dates/', views.get_available_order_dates, name='get_available_order_dates'),
    path('most_sold_category/', views.most_sold_category, name='most_sold_category'),
    
]
  

