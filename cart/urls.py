from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove/<int:product_id>/', views.remove_cart, name='remove_cart'),  # 추가
    path('delete/<int:product_id>/', views.delete_cart, name='delete_cart'),  # 여기 추가
    path('checkout/', views.checkout, name='checkout'),  # 여기 추가
]
