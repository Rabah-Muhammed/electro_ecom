from django.contrib import admin
from .models import Brand, Product, ReviewRatingz, ProductGallery
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available', 'is_featured')
    list_filter = ('category', 'is_available', 'is_featured')
    prepopulated_fields = {'slug': ('product_name',)}
    fields = ('product_name', 'slug', 'description', 'price', 'offer_percentage', 'images', 'stock', 'is_available', 'is_deleted', 'is_featured', 'category','brand')
    inlines = [ProductGalleryInline]
    
    def save_model(self, request, obj, form, change):
        # Ensure original_price is set before saving the product
        if not obj.original_price:
            obj.original_price = obj.price
        # Save the product to update the price based on the highest offer percentage
        super().save_model(request, obj, form, change)
        # Update the price based on the highest offer percentage after initial save
        obj.save()

admin.site.register(ProductGallery)
admin.site.register(Product, ProductAdmin)
admin.site.register(ReviewRatingz)
admin.site.register(Brand)