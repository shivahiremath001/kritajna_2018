# Kritajna - Quick Start Guide

## 🚀 Getting Started

Your Kritajna local commerce platform is now **fully built and ready to use**!

### Server Status

The Django development server is running at:
```
http://127.0.0.1:8000/
```

### Accessing the Platform

1. **Homepage**: http://127.0.0.1:8000/
2. **Admin Panel**: http://127.0.0.1:8000/admin/
3. **Browse Products**: http://127.0.0.1:8000/products/browse/

## 📋 Test Accounts

### Admin/Super User
- **Username**: admin
- **Password**: admin123
- **Access**: Admin panel for user and payment management

### Farmer Accounts
1. **Username**: rajesh_farmer
   - **Password**: farmer123
   - **Farmer ID (Kissan-ID)**: KISSAN001
   - **Location**: Delhi, Haryana
   - **Subscription Amount**: ₹250.00 (paid)
   - **Products**: 3 (Tomatoes, Onions, Potatoes)

2. **Username**: priya_farmer
   - **Password**: farmer123
   - **Farmer ID (Kissan-ID)**: KISSAN002
   - **Location**: Mumbai, Maharashtra
   - **Subscription Amount**: ₹500.00 (paid)
   - **Products**: 3 (Carrots, Cabbage, Spinach)

### Customer Account
- **Username**: john_customer
- **Password**: customer123
- **Location**: Bangalore, Karnataka

### Delivery Partner Account
- **Username**: arjun_delivery
- **Password**: delivery123
- **Location**: Central Hub, Delhi

## 🧪 Testing Guide

### Test as Farmer
1. Login with `rajesh_farmer / farmer123`
2. Go to **Farmer Dashboard** to see:
   - Current sales statistics
   - List of products
   - Recent orders
   - Payment history showing ₹250.00 subscription
3. Click **Add New Product** to add a new produce item
4. Edit or delete existing products
5. Check admin panel to see subscription amount tracked

### Test as Customer
1. Login with `john_customer / customer123`
2. Go to **Browse Products** to search and filter items
3. Click on any product to see details
4. Add products to create an order
5. Enter delivery location and complete order
6. Check **My Orders** dashboard to track status

### Test as Delivery Partner
1. Login with `arjun_delivery / delivery123`
2. Go to **My Deliveries** dashboard
3. View assigned orders (currently empty - orders need to be assigned from admin)
4. See pickup locations (farmers) and delivery location (customers)
5. Update order status as you progress through delivery

### Test as Admin
1. Login to admin panel: http://127.0.0.1:8000/admin/
2. **Users**: See all users with their roles and subscription amounts
3. **Products**: Browse all listed products
4. **Orders**: Track all orders placed
5. **Payments**: See subscription fees and order payments
6. **Key features**:
   - Filter users by role and subscription status
   - View **subscription_amount** field for farmers in user list view
   - Track all payment types (subscription, order, delivery_earning)

## 🎯 Key Features to Explore

### For Farmers
- ✅ Kissan-ID based authentication (KISSAN001, KISSAN002)
- ✅ Subscription payment tracking (visible in admin: ₹250, ₹500)
- ✅ Product CRUD operations
- ✅ Order dashboard showing sales
- ✅ Payment history showing subscription charges

### For Customers
- ✅ Browse products by name or location
- ✅ View complete product and farmer details
- ✅ Place orders with delivery address
- ✅ Track order status
- ✅ View order history and spending

### For Delivery Partners
- ✅ See assigned orders
- ✅ View farmer pickup locations
- ✅ View customer delivery locations
- ✅ Update delivery status
- ✅ Track earnings

### For Admin
- ✅ User role management
- ✅ Subscription amount tracking per farmer
- ✅ Product inventory management
- ✅ Order tracking and status management
- ✅ Payment history audit trail

## 📊 Project Structure

```
kritajna/
├── manage.py                 # Django management tool
├── db.sqlite3               # Database (SQLite)
├── populate_data.py         # Script to populate sample data
├── README.md                # Full documentation
├── QUICKSTART.md            # This file
│
├── kritajna/                # Project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/                   # User authentication (4 roles)
│   ├── models.py
│   ├── views.py (signup, login, dashboards)
│   ├── forms.py
│   └── admin.py
│
├── products/                # Product management
│   ├── models.py
│   ├── views.py (browse, add, edit, delete)
│   ├── forms.py
│   └── admin.py
│
├── orders/                  # Order management
│   ├── models.py (Order, OrderItem)
│   ├── views.py (create, track, deliver)
│   ├── forms.py
│   └── admin.py
│
├── payments/                # Payment tracking
│   ├── models.py
│   ├── views.py
│   └── admin.py
│
├── templates/               # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── users/ (signup, login, dashboards)
│   ├── products/ (browse, detail, add, edit, delete)
│   ├── orders/ (detail, create)
│   └── payments/ (history)
│
└── static/                  # CSS, JavaScript, images
    └── css/style.css
```

## 🔧 Common Commands

### Start Server
```bash
python manage.py runserver
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Populate Sample Data
```bash
python populate_data.py
```

### Access Django Shell
```bash
python manage.py shell
```

### Migrate Database
```bash
python manage.py makemigrations
python manage.py migrate
```

## 📝 Database Models

### User Model (Custom)
- Standard Django User fields
- **role**: customer, farmer, delivery_partner
- **Farmer-specific**: farmer_id, subscription_paid, subscription_amount
- **All users**: phone_number, location

### Product Model
- name, description, price, quantity
- farmer (ForeignKey)
- location, image, sold_out status

### Order Model
- customer, delivery_partner (ForeignKey)
- customer_location
- total_amount, delivery_charge
- status: pending, confirmed, in_delivery, delivered

### OrderItem Model
- order, product (ForeignKey)
- quantity, price (at time of order)

### Payment Model
- user (ForeignKey)
- amount, type (subscription/order/delivery_earning)
- date, description

## 🌐 URL Routes

| URL | Purpose |
|-----|---------|
| `/` | Homepage |
| `/admin/` | Django Admin Panel |
| `/signup/` | User Registration |
| `/login/` | User Login |
| `/farmer/subscription/` | Farmer Subscription |
| `/farmer/dashboard/` | Farmer Dashboard |
| `/customer/dashboard/` | Customer Dashboard |
| `/delivery/dashboard/` | Delivery Partner Dashboard |
| `/products/browse/` | Browse All Products |
| `/products/<id>/` | Product Details |
| `/products/add/` | Add Product |
| `/products/<id>/edit/` | Edit Product |
| `/orders/create/` | Create Order |
| `/orders/<id>/` | Order Details |
| `/payments/history/` | Payment History |

## 💡 Next Steps

### For Development
1. Explore the codebase in `kritajna/` directory
2. Customize templates in `templates/` folder
3. Add more styling in `static/css/style.css`
4. Integrate real payment gateway (Stripe, Razorpay)
5. Add email notifications

### For Deployment
1. Set `DEBUG = False` in settings.py
2. Configure static files and ALLOWED_HOSTS
3. Use PostgreSQL instead of SQLite
4. Deploy to Heroku, AWS, or DigitalOcean
5. Set up HTTPS/SSL certificate

### To Extend Features
1. Add product reviews and ratings
2. Implement location-based search (Google Maps API)
3. SMS/Email notifications
4. Bulk order management for farmers
5. Analytics dashboard
6. Mobile app version

## 🐛 Troubleshooting

### Server Already in Use
```bash
# Kill existing process
taskkill /F /IM python.exe

# Or use different port
python manage.py runserver 8001
```

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
rm db.sqlite3
python manage.py migrate
python populate_data.py
```

### Missing Static Files
```bash
python manage.py collectstatic --noinput
```

## 📞 Support Resources

- Django Docs: https://docs.djangoproject.com/
- Bootstrap Docs: https://getbootstrap.com/docs/
- Python Docs: https://docs.python.org/3/

## 🎉 Success!

Your **Kritajna** local commerce platform is ready! Test all features using the sample accounts, then customize it for your needs.

**Happy coding!** 🚀
