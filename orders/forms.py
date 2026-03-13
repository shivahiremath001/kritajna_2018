from django import forms
from .models import Order, OrderItem
from decimal import Decimal


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_location']
        widgets = {
            'customer_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Delivery Address'
            }),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get('product')
        quantity = cleaned.get('quantity')
        if product and quantity is not None:
            # Determine unit code/name from unit_obj if available, otherwise fallback to legacy field
            unit_code = None
            if getattr(product, 'unit_obj', None):
                unit_code = (product.unit_obj.code or product.unit_obj.name).lower()
            else:
                unit_code = (product.unit or '').lower()

            if unit_code in ('bundle', 'piece'):
                # enforce integer quantity
                try:
                    if quantity != quantity.to_integral_value():
                        raise forms.ValidationError('Quantity for this product must be a whole number')
                except AttributeError:
                    # quantity might be int/float
                    if Decimal(quantity) != Decimal(int(quantity)):
                        raise forms.ValidationError('Quantity for this product must be a whole number')

        return cleaned
