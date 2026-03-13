from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('farmer', 'Farmer'),
        ('delivery_partner', 'Delivery Partner'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    location = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # Farmer-specific fields
    farmer_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    subscription_paid = models.BooleanField(default=False)
    subscription_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subscription_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
