from django.urls import path
from . import views

app_name = 'pay'

urlpatterns = [
    path('kakao/request/', views.kakao_pay_request, name='kakao_pay_request'),
    path('kakao/success/', views.kakao_pay_approve, name='kakao_pay_success'),
    path('kakao/cancel/', views.kakao_pay_cancel, name='kakao_pay_cancel'),
    path('kakao/fail/', views.kakao_pay_fail, name='kakao_pay_fail'),
    path('', views.payment_page, name='payment_page'),
]