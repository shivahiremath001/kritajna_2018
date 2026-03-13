from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'location')}),
        ('Role Info', {'fields': ('role', 'farmer_id')}),
        ('Farmer Subscription', {'fields': ('subscription_paid', 'subscription_amount', 'subscription_date')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    list_display = ('username', 'email', 'role', 'subscription_paid', 'subscription_amount', 'phone_number')
    list_filter = ('role', 'subscription_paid', 'date_joined')
    search_fields = ('username', 'email', 'farmer_id', 'phone_number')
