from django.urls import path
from . import views

urlpatterns = [
    path('browse/', views.browse_products, name='browse_products'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('search/', views.search_results, name='search_results'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('<int:pk>/delete/', views.delete_product, name='delete_product'),
]
