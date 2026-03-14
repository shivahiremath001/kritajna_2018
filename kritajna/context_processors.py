from orders.models import Cart


def cart_item_count(request):
    """Provide `cart_item_count` in template context for authenticated customers."""
    count = 0
    try:
        if request.user.is_authenticated and getattr(request.user, 'role', None) == 'customer':
            cart, _ = Cart.objects.get_or_create(user=request.user)
            count = cart.items.count()
    except Exception:
        count = 0
    return {'cart_item_count': count}
