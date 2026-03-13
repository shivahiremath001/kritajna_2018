from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'payment_type', 'date')
    list_filter = ('payment_type', 'date', 'user')
    search_fields = ('user__username', 'description')
    readonly_fields = ('date',)
    fieldsets = (
        ('Payment Info', {'fields': ('user', 'amount', 'payment_type')}),
        ('Details', {'fields': ('description', 'date')}),
    )
