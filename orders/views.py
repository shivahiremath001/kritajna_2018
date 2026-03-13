from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Order, OrderItem
from products.models import Product
from .forms import OrderForm
from payments.models import Payment
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from .models import OrderMessage
from django.views.decorators.http import require_POST


@login_required(login_url='login')
def create_order(request):
    """Create a new order (Customers only)"""
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can create orders')
        return redirect('home')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Get selected products from POST data
            order = form.save(commit=False)
            order.customer = request.user
            order.save()
            
            # Add items to order
            product_ids = request.POST.getlist('product_id')
            quantities = request.POST.getlist('quantity')
            
            total_amount = Decimal('0.00')
            for product_id, quantity in zip(product_ids, quantities):
                if product_id and quantity:
                    try:
                        product = Product.objects.get(pk=product_id)
                        try:
                            qty = Decimal(quantity)
                        except InvalidOperation:
                            messages.error(request, f'Invalid quantity for {product.name}')
                            order.delete()
                            return redirect('browse_products')

                        # Enforce integer quantities for bundle/piece units (respect admin-managed Unit)
                        unit_code = None
                        if getattr(product, 'unit_obj', None):
                            unit_code = (product.unit_obj.code or product.unit_obj.name).lower()
                        else:
                            unit_code = (product.unit or '').lower()

                        if unit_code in ('bundle', 'piece'):
                            if qty != qty.to_integral_value():
                                messages.error(request, f'Quantity for {product.name} must be a whole number')
                                order.delete()
                                return redirect('browse_products')

                        if qty > product.quantity:
                            messages.error(request, f'Not enough stock for {product.name}')
                            order.delete()
                            return redirect('browse_products')

                        # Determine price per unit at time of ordering
                        price_unit = product.price_per_unit if product.price_per_unit and product.price_per_unit > 0 else product.price

                        # Create order item and reduce stock
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=qty,
                            price_per_unit=price_unit
                        )

                        subtotal = (qty * price_unit).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                        total_amount += subtotal

                        # Update product quantity
                        product.quantity = (product.quantity - qty)
                        if product.quantity <= 0:
                            product.sold_out = True
                            product.quantity = Decimal('0')
                        product.save()
                    except Product.DoesNotExist:
                        pass

            # Save total as Decimal
            order.total_amount = total_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            order.save()

            # Leave order as pending for farmer confirmation; farmers will see it on their dashboard
            messages.success(request, f'Order #{order.id} created successfully and is pending farmer confirmation.')
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm()
    
    # Get available products
    products = Product.objects.filter(sold_out=False)
    context = {
        'form': form,
        'products': products,
    }
    
    return render(request, 'orders/create.html', context)


@login_required(login_url='login')
def order_detail(request, pk):
    """Order detail view"""
    order = get_object_or_404(Order, pk=pk)
    
    # Check permissions
    if request.user != order.customer and request.user != order.delivery_partner:
        # Check if user is a farmer who sold items in this order
        if request.user.role == 'farmer':
            if not order.items.filter(product__farmer=request.user).exists():
                messages.error(request, 'You do not have permission to view this order')
                return redirect('home')
        else:
            messages.error(request, 'You do not have permission to view this order')
            return redirect('home')
    
    # Determine if current user may post messages on this order
    user = request.user
    can_message = False
    if user == order.customer or user == order.delivery_partner:
        can_message = True
    if getattr(user, 'role', None) == 'farmer' and order.items.filter(product__farmer=user).exists():
        can_message = True

    context = {
        'order': order,
        'can_message': can_message,
    }
    return render(request, 'orders/detail.html', context)


@login_required(login_url='login')
def assign_delivery_partner(request, pk):
    """Assign delivery partner to order (Admin/Automatic)"""
    order = get_object_or_404(Order, pk=pk)
    
    # This is simplified - in production, you might have a queue system
    # For now, the first available delivery partner is assigned
    if request.method == 'POST':
        from users.models import User
        available_partners = User.objects.filter(role='delivery_partner')[:1]
        
        if available_partners:
            order.delivery_partner = available_partners[0]
            order.status = 'confirmed'
            order.save()
            messages.success(request, 'Delivery partner assigned!')
        else:
            messages.error(request, 'No delivery partners available')
    
    return redirect('order_detail', pk=order.pk)


@login_required(login_url='login')
def delivery_partner_orders(request):
    """List orders assigned to the delivery partner for action (accept/reject)"""
    if request.user.role != 'delivery_partner':
        messages.error(request, 'Only delivery partners can access this page')
        return redirect('home')

    orders = Order.objects.filter(delivery_partner=request.user).exclude(status__in=['delivered', 'cancelled'])
    context = {'orders': orders}
    return render(request, 'orders/delivery_assigned.html', context)


@login_required(login_url='login')
def farmer_accept_order(request, pk):
    """Farmer accepts an order: set to 'confirmed' and assign delivery partner"""
    order = get_object_or_404(Order, pk=pk)
    # ensure current user is a farmer involved in this order
    if request.user.role != 'farmer' or not order.items.filter(product__farmer=request.user).exists():
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('home')

    if request.method == 'POST':
        with transaction.atomic():
            order.status = 'confirmed'
            # assign first available delivery partner (simple strategy)
            from users.models import User
            partner = User.objects.filter(role='delivery_partner', is_active=True).exclude(pk=request.user.pk).first()
            if partner:
                order.delivery_partner = partner
            order.save()
        messages.success(request, f'Order #{order.id} accepted.')
    return redirect('farmer_dashboard')


@login_required(login_url='login')
def farmer_reject_order(request, pk):
    """Farmer rejects an order: cancel and restock items belonging to this farmer"""
    order = get_object_or_404(Order, pk=pk)
    if request.user.role != 'farmer' or not order.items.filter(product__farmer=request.user).exists():
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('home')

    if request.method == 'POST':
        with transaction.atomic():
            # Restock products sold by this farmer
            for item in order.items.select_related('product'):
                prod = item.product
                # Only restock items owned by this farmer
                if prod.farmer == request.user:
                    prod.quantity += item.quantity
                    if prod.quantity > 0:
                        prod.sold_out = False
                    prod.save()

            order.status = 'cancelled'
            order.save()
            # Optionally: create refund/payment reversal (out of scope)
        messages.info(request, f'Order #{order.id} rejected and cancelled.')
    return redirect('farmer_dashboard')


@login_required(login_url='login')
def respond_delivery(request, pk, action):
    """Delivery partner accepts or rejects assigned order"""
    order = get_object_or_404(Order, pk=pk)

    if request.user.role != 'delivery_partner' or request.user != order.delivery_partner:
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('home')

    if action == 'accept':
        if order.status != 'confirmed':
            messages.error(request, 'Order is not in a state to accept')
            return redirect('delivery_orders')

        # Mark order as in_delivery
        order.status = 'in_delivery'
        order.save()
        messages.success(request, f'You accepted Order #{order.id}.')
        return redirect('delivery_orders')

    elif action == 'reject':
        # Unassign delivery partner and set back to pending so it can be reassigned
        order.delivery_partner = None
        order.status = 'pending'
        order.save()
        messages.info(request, f'You rejected Order #{order.id}. It will be reassigned.')
        return redirect('delivery_orders')

    else:
        messages.error(request, 'Invalid action')
        return redirect('delivery_orders')


@login_required(login_url='login')
@require_POST
def post_message(request, pk):
    """Post a message related to an order (customer/farmer/delivery partner)."""
    order = get_object_or_404(Order, pk=pk)
    # permission: customer, delivery_partner, or any farmer in the order
    user = request.user
    allowed = False
    if user == order.customer or user == order.delivery_partner:
        allowed = True
    if user.role == 'farmer' and order.items.filter(product__farmer=user).exists():
        allowed = True

    if not allowed:
        messages.error(request, 'You are not allowed to message on this order')
        return redirect('order_detail', pk=order.pk)

    content = request.POST.get('message', '').strip()
    if content:
        OrderMessage.objects.create(order=order, sender=user, content=content)
        messages.success(request, 'Message sent')
    else:
        messages.error(request, 'Message cannot be empty')

    return redirect('order_detail', pk=order.pk)





@login_required(login_url='login')
def update_order_status(request, pk, status):
    """Update order status"""
    order = get_object_or_404(Order, pk=pk)
    
    # Only delivery partner or admin can update status
    if request.user != order.delivery_partner and not request.user.is_staff:
        messages.error(request, 'You do not have permission to update this order')
        return redirect('home')
    
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save()
        messages.success(request, f'Order status updated to {order.get_status_display()}')
        
        # Log earnings for delivery partner
        if status == 'delivered':
            # Pay farmers their share and delivery partner. Avoid duplicating payments by checking existing descriptions.
            # Farmers: grouped by farmer
            earnings_by_farmer = {}
            for item in order.items.select_related('product__farmer'):
                farmer = item.product.farmer
                amt = (item.quantity * item.price_per_unit).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                earnings_by_farmer.setdefault(farmer, Decimal('0.00'))
                earnings_by_farmer[farmer] += amt

            for farmer, amt in earnings_by_farmer.items():
                desc = f'Earnings for Order #{order.id}'
                if not Payment.objects.filter(user=farmer, description=desc).exists():
                    Payment.objects.create(
                        user=farmer,
                        amount=amt,
                        payment_type='order',
                        description=desc
                    )

            # Delivery partner payment (guard against duplicates)
            if order.delivery_partner:
                desc = f'Delivery for Order #{order.id}'
                if not Payment.objects.filter(user=order.delivery_partner, description=desc).exists():
                    dp_amt = order.delivery_charge.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    Payment.objects.create(
                        user=order.delivery_partner,
                        amount=dp_amt,
                        payment_type='delivery_earning',
                        description=desc
                    )
    
    return redirect('order_detail', pk=order.pk)
