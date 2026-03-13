# Kritajna - Local Commerce Platform

A Django-based local commerce platform that connects **farmers (sellers)**, **customers**, and **delivery partners** in a transparent, user-friendly ecosystem.

## Features

### 👨‍🌾 For Farmers
- **Kissan-ID Based Authentication**: Secure farmer registration with farmer ID
- **Subscription Model**: Pay one-time subscription fee to list products
- **Product Management**: Add, edit, and delete produce listings
- **Order Management**: Track all orders and customer details
- **Dashboard**: View sales stats, total earnings, pending orders, and subscription amount (visible in admin panel)
- **Payment History**: Track all subscription and earnings

### 👥 For Customers
- **Browse Products**: Search and filter fresh produce by location and name
- **Product Details**: View complete product information with farmer details
- **Easy Ordering**: Add products to cart and place orders with delivery address
- **Order Tracking**: Monitor order status from pending to delivered
- **Order History**: View all past orders and spending

### 🚚 For Delivery Partners
- **Order Assignment**: Receive assigned orders for delivery
- **Location Tracking**: See pickup locations (farmers) and delivery location (customer)
- **Status Updates**: Mark orders as picked up and delivered
- **Earnings Tracking**: View total earnings from completed deliveries
- **Dashboard**: Monitor all deliveries and earnings

## Tech Stack

- **Backend**: Django 5.2
- **Database**: SQLite (default, upgradeable)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Image Handling**: Pillow
- **Server**: Django Development Server

## Project Structure

```
kritajna/
├── manage.py
├── db.sqlite3
├── kritajna/              # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── users/                 # User authentication & roles
│   ├── models.py         # Custom User model with roles
│   ├── views.py          # Auth and dashboard views
│   ├── forms.py          # Registration and login forms
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
│
├── products/             # Product management
│   ├── models.py         # Product model
│   ├── views.py          # Browse, add, edit, delete products
│   ├── forms.py          # Product forms
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
│
├── orders/              # Order management
│   ├── models.py        # Order & OrderItem models
│   ├── views.py         # Order creation, tracking, delivery
│   ├── forms.py         # Order forms
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
│
├── payments/            # Payment tracking
│   ├── models.py        # Payment model
│   ├── views.py         # Payment history
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
│
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── home.html        # Homepage
│   ├── users/
│   │   ├── signup.html
│   │   ├── login.html
│   │   ├── farmer_subscription.html
│   │   ├── farmer_dashboard.html
│   │   ├── customer_dashboard.html
│   │   └── delivery_dashboard.html
│   ├── products/
│   │   ├── browse.html
│   │   ├── detail.html
│   │   ├── add.html
│   │   ├── edit.html
│   │   └── delete.html
│   ├── orders/
│   │   └── detail.html
│   └── payments/
│       └── history.html
│
├── static/              # Static files (CSS, JS, images)
│   └── css/
│       └── style.css
│
└── media/               # User-uploaded files
    └── products/        # Product images
```

## Installation & Setup

### 1. Install Requirements

```bash
pip install django pillow
```

### 2. Create Database

```bash
python manage.py migrate
```

### 3. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Default admin created during setup:
- **Username**: admin
- **Password**: admin123
- **Email**: admin@kritajna.local

### 4. Start Server

```bash
python manage.py runserver
```

The platform will be available at: `http://127.0.0.1:8000/`

## Usage Guide

### For Farmers

1. **Sign Up**: Click "Sign Up" → Select "Farmer" role → Enter Kissan-ID
2. **Subscribe**: Complete subscription payment (₹100, ₹250, ₹500, or ₹900)
3. **Add Products**: Go to dashboard → "Add New Product"
4. **Manage Orders**: Monitor orders and mark them as ready for delivery
5. **Track Earnings**: View payment history showing subscription and order details

### For Customers

1. **Sign Up**: Click "Sign Up" → Select "Customer" role
2. **Browse Products**: Search by product name or location
3. **Place Order**: Click product → Add to order → Enter delivery address
4. **Track Orders**: Monitor order status in your dashboard
5. **View History**: Access payment history for order receipts

### For Delivery Partners

1. **Sign Up**: Click "Sign Up" → Select "Delivery Partner" role
2. **Accept Deliveries**: Dashboard shows assigned orders with pickup & delivery locations
3. **Update Status**: Mark orders as "In Delivery" → "Delivered"
4. **Track Earnings**: View delivery charges and total earnings

## Admin Panel Access

Visit: `http://127.0.0.1:8000/admin/`

**Login**: admin / admin123

### Key Admin Features

- **User Management**: View all users with roles, subscription status, and deposited amounts
- **Products**: Monitor all listed products, farmer details, and stock status
- **Orders**: Track all orders, customer locations, payments, and delivery partners
- **Payments**: Complete payment history including subscriptions, orders, and delivery earnings

### Important Admin Fields

- **Users**: Shows `subscription_amount` field for farmer deposits (visible in list view)
- **Products**: Filter by farmer, view sold out status
- **Orders**: Assign delivery partners, track order status and amounts
- **Payments**: Track money flow (subscriptions, orders, earnings)

## Database Models

### User Model
- Custom Django User model with roles: Customer, Farmer, Delivery Partner
- Farmer-specific fields: `farmer_id`, `subscription_paid`, `subscription_amount`, `subscription_date`

### Product Model
- `name`, `description`, `price`, `quantity`
- `location` (farmer's location), `image`
- `sold_out` status tracking

### Order Model
- Links customer, delivery partner, and multiple products
- `customer_location` for delivery
- `total_amount`, `delivery_charge` (₹50 default)
- Order status: Pending → Confirmed → In Delivery → Delivered

### Payment Model
- Tracks subscriptions, order payments, and delivery earnings
- Payment type: 'subscription', 'order', 'delivery_earning'

## URL Routes

| Route | Purpose |
|-------|---------|
| `/` | Homepage |
| `/signup/` | User registration |
| `/login/` | User login |
| `/logout/` | User logout |
| `/farmer/subscription/` | Farmer subscription payment |
| `/farmer/dashboard/` | Farmer dashboard |
| `/customer/dashboard/` | Customer orders |
| `/delivery/dashboard/` | Delivery partner orders |
| `/products/browse/` | Browse all products |
| `/products/<id>/` | Product details |
| `/products/add/` | Add new product (farmers) |
| `/products/<id>/edit/` | Edit product |
| `/products/<id>/delete/` | Delete product |
| `/orders/create/` | Create new order |
| `/orders/<id>/` | Order details |
| `/payments/history/` | Payment history |
| `/admin/` | Django admin panel |

## Customization Tips

### Change Delivery Charge
Edit `kritajna/settings.py` or modify in order creation:
```python
order.delivery_charge = 50.00  # Change to desired amount
```

### Modify Subscription Plans
Edit in `users/forms.py` - `FarmerSubscriptionForm.SUBSCRIPTION_CHOICES`

### Add Payment Gateway Integration
Replace simulated payments in `users/views.py` with:
- Stripe
- Razorpay
- PayPal
- Other providers

### Customize Styling
Edit `static/css/style.css` to match your branding

## Future Enhancements

- [ ] Real payment gateway integration (Stripe, Razorpay)
- [ ] Google Maps integration for location tracking
- [ ] SMS notifications for orders
- [ ] Email notifications
- [ ] Product ratings and reviews
- [ ] Farmer analytics and insights
- [ ] Mobile app
- [ ] Advanced search with filters
- [ ] Wishlist functionality
- [ ] Bulk order management

## Support

For issues or questions, create an issue in the project repository.

## License

This project is open source and available under the MIT License.

---

**Build by**: GitHub Copilot
**Version**: 1.0.0
**Last Updated**: March 2026
