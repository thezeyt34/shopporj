from django.urls import path
from .views import *

urlpatterns = [
    # ---------- MAIN ----------
    path('', home_view, name='home'),
    path('product/<int:product_id>/', detail_view, name='detail'),

    # ---------- CART ----------
    path('cart/', cart_view, name='cart'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', remove_item, name='remove_item'),
    path('clear/', clear_cart, name='clear_cart'),
    path('update/<int:product_id>/', update_quantity, name='update_quantity'),

    # ---------- CHECKOUT ----------
    path('checkout/', checkout_view, name='checkout'),
    path('create-order/', create_order, name='create_order'),
    path('success/<str:order_code>/', success_view, name='success'),

    # ---------- ADMIN ----------
    path('admin-login/', admin_login, name='admin_login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin-logout/', admin_logout, name='admin_logout'),

    # ---------- BUYURTMALAR (НОВОЕ) ----------
    path('orders/', orders_view, name='orders'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:order_id>/status/', change_status, name='change_status'),
        # MIJOZLAR
    path('customers/', customers_view, name='customers'),

    # PRODUCTS
    path('products/', products_view, name='products'),
    path('products/delete/<int:id>/', delete_product, name='delete_product'),
    path('products/edit/<int:id>/', edit_product, name='edit_product'),

    # CATEGORIES
# CATEGORIES
    path('categories/', categories_view, name='categories'),
    path('categories/add/', add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', edit_category, name='edit_category'),
    path('categories/delete/<int:id>/', delete_category, name='delete_category'),
    # PRODUCTS
    path('products/add/', add_product, name='add_product'),
    path('products/edit/<int:id>/', edit_product, name='edit_product'),
    path('finance/', finance_view, name='finance'),
]