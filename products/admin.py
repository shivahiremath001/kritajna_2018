from django.contrib import admin
from .models import Product, Category, Unit


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'category', 'display_unit', 'price', 'quantity', 'sold_out', 'location', 'created_at')
    list_filter = ('sold_out', 'created_at', 'farmer', 'category')
    search_fields = ('name', 'description', 'farmer__username', 'category__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Product Info', {'fields': ('farmer', 'name', 'description', 'price', 'price_per_unit', 'unit_obj', 'unit', 'quantity', 'category')}),
        ('Location & Status', {'fields': ('location', 'sold_out')}),
        ('Media', {'fields': ('image',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def display_unit(self, obj):
        return obj.unit_obj.code or obj.unit_obj.name if obj.unit_obj else obj.unit
    display_unit.short_description = 'Unit'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'code')
    prepopulated_fields = {"slug": ("name",)}
