from django.contrib import admin
from .models import Product, ProductImage, OrderItem, Order, CartItem, Cart, Category


# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'inventory', 'is_active', 'created_at']
    list_filter = ['is_active', 'category']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline]


admin.site.register([Cart, CartItem, Order, OrderItem])
