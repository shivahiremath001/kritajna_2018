from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/assign-delivery/', views.assign_delivery_partner, name='assign_delivery'),
    path('<int:pk>/update-status/<str:status>/', views.update_order_status, name='update_order_status'),
    path('delivery/', views.delivery_partner_orders, name='delivery_orders'),
    path('delivery/<int:pk>/<str:action>/', views.respond_delivery, name='respond_delivery'),
    path('farmer/<int:pk>/accept/', views.farmer_accept_order, name='farmer_accept_order'),
    path('farmer/<int:pk>/reject/', views.farmer_reject_order, name='farmer_reject_order'),
    # Per-item farmer actions
    path('farmer/item/<int:item_pk>/accept/', views.farmer_accept_item, name='farmer_accept_item'),
    path('farmer/item/<int:item_pk>/reject/', views.farmer_reject_item, name='farmer_reject_item'),
    path('<int:pk>/message/', views.post_message, name='post_order_message'),
]
