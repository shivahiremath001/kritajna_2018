from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Order, OrderItem
from .models import Cart
from products.models import Product
from .forms import OrderForm
from payments.models import Payment
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from .models import OrderMessage
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponseForbidden


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
def cart_view(request):
    if request.user.role != 'customer':
        messages.error(request, 'Only customers have carts')
        return redirect('home')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    context = {'cart': cart}
    return render(request, 'orders/cart.html', context)


@login_required(login_url='login')
def remove_from_cart(request, pk):
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can modify the cart')
        return redirect('home')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, pk=pk)
    cart.remove_product(product)
    messages.info(request, f'Removed {product.name} from cart')
    return redirect('cart_view')


@login_required(login_url='login')
def checkout(request):
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can checkout')
        return redirect('home')

    cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        customer_location = request.POST.get('customer_location', '').strip()
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty')
            return redirect('cart_view')

        if not customer_location:
            messages.error(request, 'Please provide a delivery location')
            return redirect('cart_view')

        try:
            order = cart.create_order(customer_location=customer_location)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('cart_view')

        messages.success(request, f'Order #{order.id} created successfully')
        return redirect('order_detail', pk=order.pk)

    # GET: show simple checkout form on cart page
    return redirect('cart_view')


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
        # Farmer accepts all pending items in this order that belong to them
        accepted_items = []
        with transaction.atomic():
            items = order.items.select_related('product').filter(product__farmer=request.user, status=OrderItem.STATUS_PENDING)
            for item in items:
                try:
                    item.accept_by_farmer(request.user)
                    accepted_items.append(item)
                except PermissionError:
                    continue

            # Recalculate order total based on accepted items (final billed amount)
            order.total_amount = order.calculate_total(accepted_only=True)

            # If no items are pending (all accepted or rejected), mark order confirmed and assign delivery partner
            if not order.items.filter(status=OrderItem.STATUS_PENDING).exists():
                order.status = 'confirmed'
                from users.models import User
                partner = User.objects.filter(role='delivery_partner', is_active=True).exclude(pk=request.user.pk).first()
                if partner:
                    order.delivery_partner = partner

            order.save()

        messages.success(request, f'Accepted {len(accepted_items)} item(s) in Order #{order.id}.')
    return redirect('farmer_dashboard')


@login_required(login_url='login')
def farmer_reject_order(request, pk):
    """Farmer rejects an order: cancel and restock items belonging to this farmer"""
    order = get_object_or_404(Order, pk=pk)
    if request.user.role != 'farmer' or not order.items.filter(product__farmer=request.user).exists():
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('home')

    if request.method == 'POST':
        # Farmer rejects only their items; restock those items and update order total
        rejected_count = 0
        with transaction.atomic():
            items = order.items.select_related('product').filter(product__farmer=request.user, status=OrderItem.STATUS_PENDING)
            for item in items:
                try:
                    item.reject_by_farmer(request.user)
                    rejected_count += 1
                except PermissionError:
                    continue

            # Recalculate order total based on accepted items (final billed amount)
            order.total_amount = order.calculate_total(accepted_only=True)

            # Do not cancel entire order; keep status pending until all farmers respond
            # If all items rejected, cancel the order
            if not order.items.exclude(status=OrderItem.STATUS_REJECTED).exists():
                order.status = 'cancelled'
            order.save()

        messages.info(request, f'Rejected {rejected_count} item(s) in Order #{order.id}.')
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
def farmer_accept_item(request, item_pk):
    """Accept a single OrderItem by its farmer."""
    item = get_object_or_404(OrderItem, pk=item_pk)
    order = item.order
    if request.user.role != 'farmer' or item.product.farmer != request.user:
        return HttpResponseForbidden('Not allowed')

    if request.method == 'POST':
        try:
            item.accept_by_farmer(request.user)
        except PermissionError:
            messages.error(request, 'Not allowed to accept this item')
            return redirect('farmer_dashboard')

        # Recalculate order total (accepted items only) and possibly confirm whole order
        order.total_amount = order.calculate_total(accepted_only=True)
        if not order.items.filter(status=OrderItem.STATUS_PENDING).exists():
            order.status = 'confirmed'
            # assign delivery partner if missing
            from users.models import User
            partner = User.objects.filter(role='delivery_partner', is_active=True).exclude(pk=request.user.pk).first()
            if partner:
                order.delivery_partner = partner
        order.save()
        messages.success(request, 'Item accepted')
    return redirect('farmer_dashboard')


@login_required(login_url='login')
def farmer_reject_item(request, item_pk):
    """Reject a single OrderItem by its farmer."""
    item = get_object_or_404(OrderItem, pk=item_pk)
    order = item.order
    if request.user.role != 'farmer' or item.product.farmer != request.user:
        return HttpResponseForbidden('Not allowed')

    if request.method == 'POST':
        try:
            item.reject_by_farmer(request.user)
        except PermissionError:
            messages.error(request, 'Not allowed to reject this item')
            return redirect('farmer_dashboard')

        order.total_amount = order.calculate_total(accepted_only=True)
        # If all items rejected, cancel order
        if not order.items.exclude(status=OrderItem.STATUS_REJECTED).exists():
            order.status = 'cancelled'
        order.save()
        messages.success(request, 'Item rejected and restocked')
    return redirect('farmer_dashboard')


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
            for item in order.items.select_related('product__farmer').filter(status=OrderItem.STATUS_ACCEPTED):
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
