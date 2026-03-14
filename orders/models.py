from decimal import Decimal
from django.db import models, transaction
from users.models import User
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_delivery', 'In Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', limit_choices_to={'role': 'customer'})
    delivery_partner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries', limit_choices_to={'role': 'delivery_partner'})
    
    customer_location = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"
    
    def calculate_total(self, accepted_only=False):
        """
        Calculate order total.
        - If accepted_only is True, sum only items accepted by farmers (final billed amount).
        - If False, sum all items except those explicitly rejected (initial order total at checkout).
        """
        if accepted_only:
            items = self.items.filter(status=OrderItem.STATUS_ACCEPTED)
        else:
           items = self.items.exclude(status=OrderItem.STATUS_REJECTED)
        items_total = sum(item.get_subtotal() for item in items)
        if items_total == 0:
            return 0
        return items_total + self.delivery_charge
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # allow fractional quantities like 0.5 kg
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)  # price per unit at time of order
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    def get_subtotal(self):
        return self.quantity * self.price_per_unit

    def get_accepted_subtotal(self):
        if self.status == self.STATUS_ACCEPTED:
            return self.get_subtotal()
        return Decimal('0.00')

    def accept_by_farmer(self, farmer_user):
        # Only the farmer who owns the product can accept
        if self.product.farmer != farmer_user:
            raise PermissionError('User not allowed to accept this item')
        self.status = self.STATUS_ACCEPTED
        self.save()

    def reject_by_farmer(self, farmer_user):
        # Only the farmer who owns the product can reject
        if self.product.farmer != farmer_user:
            raise PermissionError('User not allowed to reject this item')
        # mark rejected and restock
        self.status = self.STATUS_REJECTED
        self.save()
        # Restock product
        prod = self.product
        if prod.quantity is None:
            prod.quantity = self.quantity
        else:
            prod.quantity = prod.quantity + self.quantity
        if prod.quantity > 0:
            prod.sold_out = False
        prod.save()

    def __str__(self):
        return f"{self.product.name} (x{self.quantity} {self.product.unit})"


class Cart(models.Model):
    """Per-user cart. Use `Cart.objects.get_or_create(user=request.user)` in views."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)

    def add_product(self, product, quantity=1):
        quantity = Decimal(str(quantity))
        item, created = CartItem.objects.get_or_create(cart=self, product=product, defaults={'quantity': quantity})
        if not created:
            item.quantity = item.quantity + quantity
            item.save()
        return item

    def remove_product(self, product):
        CartItem.objects.filter(cart=self, product=product).delete()

    def clear(self):
        self.items.all().delete()

    @property
    def items_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    @property
    def total(self):
        return self.items_total + self.delivery_charge

    def create_order(self, customer_location, delivery_partner=None):
        """Atomically convert cart into an Order and clear the cart."""
        with transaction.atomic():
            # ensure cart is not empty
            items = list(self.items.select_related('product').select_for_update())
            if not items:
                raise ValueError('Cart is empty')

            # create order
            order = Order.objects.create(
                customer=self.user,
                delivery_partner=delivery_partner,
                customer_location=customer_location,
                delivery_charge=self.delivery_charge,
                total_amount=Decimal('0.00')
            )

            # validate stock and create order items, reduce stock
            for ci in items:
                prod = ci.product
                qty = Decimal(ci.quantity)
                if prod.quantity is not None and qty > prod.quantity:
                    # rollback
                    raise ValueError(f'Not enough stock for {prod.name}')

                price_unit = prod.price_per_unit if prod.price_per_unit and prod.price_per_unit > 0 else prod.price

                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    price_per_unit=price_unit
                )

                # reduce stock
                if prod.quantity is not None:
                    prod.quantity = prod.quantity - qty
                    if prod.quantity <= 0:
                        prod.sold_out = True
                        prod.quantity = Decimal('0')
                    prod.save()

            order.total_amount = order.calculate_total()
            order.save()
            self.clear()
            return order


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    def get_subtotal(self):
        # Use product.price_per_unit when available, otherwise fall back to product.price
        price = getattr(self.product, 'price_per_unit', None)
        if not price or price <= 0:
            price = getattr(self.product, 'price', Decimal('0.00'))
        return self.quantity * Decimal(price)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class OrderMessage(models.Model):
    """Simple message model for communication between customer, farmer and delivery partner."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message by {self.sender.username} on Order #{self.order.id}"
