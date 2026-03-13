from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from django.db.models import Sum, Count
from .models import User
from .forms import UserSignUpForm, UserLoginForm, FarmerSubscriptionForm
from products.models import Product
from products.models import Category
from orders.models import Order, OrderItem
from payments.models import Payment


def home(request):
    """Homepage"""
    categories = Category.objects.all()[:12]
    return render(request, 'home.html', {'categories': categories})


def signup(request):
    """User signup view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # If farmer, redirect to subscription
            if user.role == 'farmer':
                login(request, user)
                return redirect('farmer_subscription')
            else:
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('home')
    else:
        form = UserSignUpForm()
    
    return render(request, 'users/signup.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')


@login_required(login_url='login')
def farmer_subscription(request):
    """Farmer subscription payment view"""
    if request.user.role != 'farmer':
        messages.error(request, 'Only farmers can access this page')
        return redirect('home')
    
    if request.user.subscription_paid:
        messages.info(request, 'You already have an active subscription')
        return redirect('farmer_dashboard')
    
    if request.method == 'POST':
        form = FarmerSubscriptionForm(request.POST)
        if form.is_valid():
            subscription_amount = int(form.cleaned_data['subscription_plan'])
            
            # Process payment (simplified - in production use Stripe/Razorpay)
            request.user.subscription_paid = True
            request.user.subscription_amount = subscription_amount
            request.user.subscription_date = now()
            request.user.save()
            
            # Log payment
            Payment.objects.create(
                user=request.user,
                amount=subscription_amount,
                payment_type='subscription',
                description=f'Farmer subscription for ₹{subscription_amount}'
            )
            
            messages.success(request, f'Subscription activated! ₹{subscription_amount} charged.')
            return redirect('farmer_dashboard')
    else:
        form = FarmerSubscriptionForm()
    
    return render(request, 'users/farmer_subscription.html', {'form': form})


@login_required(login_url='login')
def farmer_dashboard(request):
    """Farmer dashboard"""
    if request.user.role != 'farmer':
        messages.error(request, 'Only farmers can access this page')
        return redirect('home')
    
    if not request.user.subscription_paid:
        return redirect('farmer_subscription')
    
    # Get farmer's products
    products = Product.objects.filter(farmer=request.user)
    
    # Get farmer's orders
    orders = Order.objects.filter(items__product__farmer=request.user).distinct()
    
    # Calculate sales stats
    total_sales = orders.filter(status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    
    # Get payments
    payments = Payment.objects.filter(user=request.user)
    
    context = {
        'products': products,
        'orders': orders,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'payments': payments,
    }
    
    return render(request, 'users/farmer_dashboard.html', context)


@login_required(login_url='login')
def customer_dashboard(request):
    """Customer dashboard"""
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can access this page')
        return redirect('home')
    
    # Get customer's orders
    orders = Order.objects.filter(customer=request.user)
    
    # Get statistics
    total_orders = orders.count()
    total_spent = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
    }
    
    return render(request, 'users/customer_dashboard.html', context)


@login_required(login_url='login')
def delivery_partner_dashboard(request):
    """Delivery partner dashboard"""
    if request.user.role != 'delivery_partner':
        messages.error(request, 'Only delivery partners can access this page')
        return redirect('home')
    
    # Get assigned orders
    orders = Order.objects.filter(delivery_partner=request.user)
    
    # Calculate earnings
    completed_orders = orders.filter(status='delivered')
    total_earnings = completed_orders.aggregate(Sum('delivery_charge'))['delivery_charge__sum'] or 0
    total_deliveries = completed_orders.count()
    pending_deliveries = orders.exclude(status__in=['delivered', 'cancelled']).count()
    
    context = {
        'orders': orders,
        'total_earnings': total_earnings,
        'total_deliveries': total_deliveries,
        'pending_deliveries': pending_deliveries,
    }
    
    return render(request, 'users/delivery_dashboard.html', context)
