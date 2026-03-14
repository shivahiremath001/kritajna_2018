from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category
from .forms import ProductForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from orders.models import Cart


def browse_products(request):
    """Browse all available products"""
    products = Product.objects.filter(sold_out=False)
    
    # Search functionality
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query)
        )
    
    # Filter by location
    location = request.GET.get('location', '')
    if location:
        products = products.filter(location__icontains=location)
    
    context = {
        'products': products,
        'query': query,
        'location': location,
    }
    
    return render(request, 'products/browse.html', context)


def category_detail(request, slug):
    """List products for a given category"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, sold_out=False)
    context = {'category': category, 'products': products}
    return render(request, 'products/category.html', context)


def search_results(request):
    q = request.GET.get('q', '').strip()
    products = Product.objects.filter(sold_out=False)
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q)
        )
    context = {'products': products, 'query': q}
    return render(request, 'products/search_results.html', context)


def product_detail(request, pk):
    """Product detail view"""
    product = get_object_or_404(Product, pk=pk)
    context = {'product': product}
    return render(request, 'products/detail.html', context)


@login_required(login_url='login')
def add_to_cart(request, pk):
    """Add a product to the current user's cart."""
    product = get_object_or_404(Product, pk=pk)
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can add products to cart')
        return redirect('product_detail', pk=pk)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    qty = request.POST.get('quantity', '1') if request.method == 'POST' else request.GET.get('quantity', '1')
    try:
        cart.add_product(product, qty)
        messages.success(request, f'Added {product.name} to cart')
    except Exception:
        messages.error(request, 'Could not add product to cart')

    return redirect('browse_products')


@login_required(login_url='login')
def add_product(request):
    """Add new product (Farmers only)"""
    if request.user.role != 'farmer':
        messages.error(request, 'Only farmers can add products')
        return redirect('browse_products')
    
    if not request.user.subscription_paid:
        messages.error(request, 'Please activate your subscription first')
        return redirect('farmer_subscription')
    
    category_count = Category.objects.count()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('farmer_dashboard')
    else:
        form = ProductForm()
    
    return render(request, 'products/add.html', {'form': form, 'category_count': category_count})


@login_required(login_url='login')
def edit_product(request, pk):
    """Edit product (Farmers only)"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.user != product.farmer:
        messages.error(request, 'You can only edit your own products')
        return redirect('farmer_dashboard')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('farmer_dashboard')
    else:
        form = ProductForm(instance=product)
    category_count = Category.objects.count()
    return render(request, 'products/edit.html', {'form': form, 'product': product, 'category_count': category_count})


@login_required(login_url='login')
def delete_product(request, pk):
    """Delete product (Farmers only)"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.user != product.farmer:
        messages.error(request, 'You can only delete your own products')
        return redirect('farmer_dashboard')
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('farmer_dashboard')
    
    return render(request, 'products/delete.html', {'product': product})
