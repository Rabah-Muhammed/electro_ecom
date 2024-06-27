
from django.urls import path
from . import views

urlpatterns = [
    path('products/',views.store,name="products"),
    path('products/<slug:category_slug>/', views.store, name='products_by_category'),
    path('products/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('submit_review/<int:product_id>/',views.submit_review,name='submit_review'),
     
]


