from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price_per_unit',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_amount', 'status', 'delivery_partner', 'created_at')
    list_filter = ('status', 'created_at', 'delivery_partner')
    search_fields = ('customer__username', 'id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {'fields': ('customer', 'customer_location', 'id')}),
        ('Delivery', {'fields': ('delivery_partner', 'delivery_charge')}),
        ('Amount', {'fields': ('total_amount',)}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price_per_unit')
    list_filter = ('order__created_at',)
    search_fields = ('product__name', 'order__id')
