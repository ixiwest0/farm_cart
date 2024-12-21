from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=255)  # 상품 이름
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 상품 가격
    stock = models.PositiveIntegerField()  # 재고
    seller = models.ForeignKey(User, on_delete=models.CASCADE)  # 판매자
    sales = models.PositiveIntegerField(default=0)  # 판매량

    def __str__(self):
        return self.name


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # 주문한 상품
    quantity = models.PositiveIntegerField()  # 주문 수량
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # 총 주문 금액
    order_date = models.DateTimeField(auto_now_add=True)  # 주문 날짜

    def __str__(self):
        return f"Order {self.id} - {self.product.name}"
