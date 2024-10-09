from django.contrib import admin

from orders.models import Order, Payment, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'is_ordered', 'variations')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'email', 'phone', 'city', 'order_total', 'status', 'is_ordered', 'created_at')
    list_filter = ('status', 'is_ordered')
    search_fields = ('order_number', 'full_name', 'email', 'phone', 'city')
    list_per_page = 20
    inlines = [OrderProductInline]


# Register your models here.
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)