from django.contrib import admin
from .models import Category

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug', 'offer_percentage', 'is_deleted')
    fields = ('category_name', 'slug', 'description', 'cat_image', 'offer_percentage', 'is_deleted')

admin.site.register(Category, CategoryAdmin)
