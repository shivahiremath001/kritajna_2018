from django import forms
from .models import Product
from .models import Category
from django.core.exceptions import ValidationError


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Show only one clear price field to farmers: price_per_unit. Keep legacy `price` on model for compatibility.
        fields = ['name', 'description', 'price_per_unit', 'unit_obj', 'quantity', 'location', 'category', 'image', 'sold_out']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Product Description', 'rows': 4}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price per unit (₹)', 'step': '0.01'}),
            'unit_obj': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity', 'step': '0.01', 'min': '0'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'sold_out': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        # Ensure legacy `price` remains populated for compatibility (set to price_per_unit when provided)
        instance = super().save(commit=False)
        if instance.price_per_unit and (not instance.price or instance.price == 0):
            instance.price = instance.price_per_unit
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get('category')
        unit_obj = cleaned.get('unit_obj')
        # If categories exist in the system, require selecting one
        if Category.objects.exists() and not category:
            raise ValidationError('Please select a category for this product.')
        # If units exist in the system, require selecting one
        from .models import Unit
        if Unit.objects.exists() and not unit_obj:
            raise ValidationError('Please select a unit for this product.')
        return cleaned
