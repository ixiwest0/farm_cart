from django.db import models
from django.contrib.auth.models import User

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 결제 사용자
    order_id = models.CharField(max_length=100, unique=True)  # 주문 번호
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # 결제 금액
    payment_status = models.CharField(max_length=50, default='pending')  # 결제 상태
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return f"Payment {self.order_id} - {self.user.username}"
