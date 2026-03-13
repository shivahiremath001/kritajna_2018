#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kritajna.settings')
django.setup()

from users.models import User
from products.models import Product, Category
from django.utils.text import slugify

print("Creating sample test data...\n")

# Create a test farmer
if not User.objects.filter(username='rajesh_farmer').exists():
    farmer = User.objects.create_user(
        username='rajesh_farmer',
        email='rajesh@kritajna.local',
        password='farmer123',
        first_name='Rajesh',
        last_name='Kumar',
        role='farmer',
        farmer_id='KISSAN001',
        phone_number='9876543210',
        location='Delhi, Haryana',
        subscription_paid=True,
        subscription_amount=250.00
    )
    print(f"✓ Created farmer: {farmer.username} (Kissan-ID: {farmer.farmer_id})")
    
    # Add products for this farmer
    products_data = [
        {'name': 'Fresh Tomatoes', 'description': 'Fresh organic red tomatoes from local farm', 'price': 40.00, 'quantity': 50, 'location': 'Delhi, Haryana'},
        {'name': 'Onions', 'description': 'High quality onions, fresh harvest', 'price': 30.00, 'quantity': 100, 'location': 'Delhi, Haryana'},
        {'name': 'Potatoes', 'description': 'Premium quality potatoes', 'price': 25.00, 'quantity': 80, 'location': 'Delhi, Haryana'},
    ]
    
    for product_data in products_data:
        Product.objects.create(
            farmer=farmer,
            name=product_data['name'],
            description=product_data['description'],
            price=product_data['price'],
            quantity=product_data['quantity'],
            location=product_data['location'],
            sold_out=False
        )
        print(f"  └─ Added product: {product_data['name']} (₹{product_data['price']})")

# Create another test farmer
if not User.objects.filter(username='priya_farmer').exists():
    farmer2 = User.objects.create_user(
        username='priya_farmer',
        email='priya@kritajna.local',
        password='farmer123',
        first_name='Priya',
        last_name='Singh',
        role='farmer',
        farmer_id='KISSAN002',
        phone_number='9876543211',
        location='Mumbai, Maharashtra',
        subscription_paid=True,
        subscription_amount=500.00
    )
    print(f"✓ Created farmer: {farmer2.username} (Kissan-ID: {farmer2.farmer_id})")
    
    products_data = [
        {'name': 'Carrots', 'description': 'Fresh orange carrots, rich in beta carotene', 'price': 50.00, 'quantity': 60, 'location': 'Mumbai, Maharashtra'},
        {'name': 'Cabbage', 'description': 'Fresh green cabbage', 'price': 20.00, 'quantity': 90, 'location': 'Mumbai, Maharashtra'},
        {'name': 'Spinach Bundle', 'description': 'Fresh organic spinach', 'price': 35.00, 'quantity': 40, 'location': 'Mumbai, Maharashtra'},
    ]
    
    for product_data in products_data:
        Product.objects.create(
            farmer=farmer2,
            name=product_data['name'],
            description=product_data['description'],
            price=product_data['price'],
            quantity=product_data['quantity'],
            location=product_data['location'],
            sold_out=False
        )
        print(f"  └─ Added product: {product_data['name']} (₹{product_data['price']})")

# Create a test customer
if not User.objects.filter(username='john_customer').exists():
    customer = User.objects.create_user(
        username='john_customer',
        email='john@kritajna.local',
        password='customer123',
        first_name='John',
        last_name='Doe',
        role='customer',
        phone_number='9876543212',
        location='Bangalore, Karnataka'
    )
    print(f"✓ Created customer: {customer.username}")

# Create a test delivery partner
if not User.objects.filter(username='arjun_delivery').exists():
    delivery = User.objects.create_user(
        username='arjun_delivery',
        email='arjun@kritajna.local',
        password='delivery123',
        first_name='Arjun',
        last_name='Sharma',
        role='delivery_partner',
        phone_number='9876543213',
        location='Central Hub, Delhi'
    )
    print(f"✓ Created delivery partner: {delivery.username}")

# Create some default categories
default_categories = [
    {'name': 'Vegetables', 'slug': 'vegetables'},
    {'name': 'Fruits', 'slug': 'fruits'},
    {'name': 'Grains', 'slug': 'grains'},
    {'name': 'Dairy', 'slug': 'dairy'},
    {'name': 'Herbs', 'slug': 'herbs'},
]

for cat in default_categories:
    obj, created = Category.objects.get_or_create(slug=cat['slug'], defaults={'name': cat['name']})
    if created:
        print(f"✓ Created category: {obj.name}")

# Assign categories to existing products that don't have one yet
keyword_map = {
    'tomato': 'vegetables',
    'onion': 'vegetables',
    'potato': 'vegetables',
    'carrot': 'vegetables',
    'cabbage': 'vegetables',
    'spinach': 'vegetables',
    'apple': 'fruits',
    'mango': 'fruits',
    'rice': 'grains',
    'wheat': 'grains',
    'milk': 'dairy',
    'cheese': 'dairy',
    'herb': 'herbs',
    'mint': 'herbs',
}

for prod in Product.objects.filter(category__isnull=True):
    assigned = False
    name_lower = prod.name.lower()
    for kw, slug in keyword_map.items():
        if kw in name_lower:
            cat = Category.objects.filter(slug=slug).first()
            if cat:
                prod.category = cat
                prod.save()
                print(f"Assigned category '{cat.name}' to product '{prod.name}'")
                assigned = True
                break
    if not assigned:
        # default to Vegetables
        veg = Category.objects.filter(slug='vegetables').first()
        if veg:
            prod.category = veg
            prod.save()
            print(f"Assigned default category 'Vegetables' to product '{prod.name}'")

print("\n" + "="*60)
print("✓ Sample data created successfully!")
print("="*60)
print("\n--- Test Accounts ---\n")
print("👨‍🌾 Farmer 1: rajesh_farmer / farmer123 (Kissan-ID: KISSAN001)")
print("  Location: Delhi, Haryana | Subscription: ₹250.00")
print("\n👨‍🌾 Farmer 2: priya_farmer / farmer123 (Kissan-ID: KISSAN002)")
print("  Location: Mumbai, Maharashtra | Subscription: ₹500.00")
print("\n👥 Customer: john_customer / customer123")
print("  Location: Bangalore, Karnataka")
print("\n🚚 Delivery Partner: arjun_delivery / delivery123")
print("  Location: Central Hub, Delhi")
print("\n🔐 Admin: admin / admin123")
print("  Admin Panel URL: http://127.0.0.1:8000/admin/")
print("\n" + "="*60)
print("\n🚀 Ready to test! Visit: http://127.0.0.1:8000/")
print("="*60 + "\n")
