from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/seller/<int:seller_id>/', consumers.SellerConsumer.as_asgi()),
]
