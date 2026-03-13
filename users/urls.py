from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('farmer/subscription/', views.farmer_subscription, name='farmer_subscription'),
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('delivery/dashboard/', views.delivery_partner_dashboard, name='delivery_dashboard'),
]
