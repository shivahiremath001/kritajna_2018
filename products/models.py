from django.db import models
from users.models import User


class Product(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'farmer'}, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    # Price information: price_per_unit represents cost for one unit (e.g. ₹30 per kg)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    UNIT_KG = 'kg'
    UNIT_LITER = 'liter'
    UNIT_BUNDLE = 'bundle'
    UNIT_PIECE = 'piece'
    UNIT_CHOICES = [
        (UNIT_KG, 'kg'),
        (UNIT_LITER, 'liter'),
        (UNIT_BUNDLE, 'bundle'),
        (UNIT_PIECE, 'piece'),
    ]

    # Legacy unit field kept for compatibility; prefer `unit_obj` when present.
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default=UNIT_KG)
    unit_obj = models.ForeignKey('Unit', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    # Quantity in stock — use Decimal to support fractional stock for kg/liter
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    sold_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Category will be nullable to avoid breaking existing products
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    def __str__(self):
        return f"{self.name} by {self.farmer.username}"
    
    class Meta:
        ordering = ['-created_at']


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Unit(models.Model):
    """Manageable units (kg, liter, bundle, piece, etc.)"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    # Optional short code used in displays (e.g., 'kg', 'L')
    code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
