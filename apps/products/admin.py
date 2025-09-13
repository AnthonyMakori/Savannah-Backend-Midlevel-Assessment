from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'sku', 'is_active')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'description', 'sku')