from django.contrib import admin

from store.models import Product


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'price', 'stock', 'category', 'modified_at', 'is_available')


# Register your models here.
admin.site.register(Product, ProductAdmin)