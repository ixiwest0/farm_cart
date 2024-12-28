import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from .models import Payment
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from cart.views import _cart_id

KAKAO_PAY_URL = "https://kapi.kakao.com/v1/payment/ready"
KAKAO_ADMIN_KEY = ""  # 카카오 개발자 콘솔에서 발급된 Admin Key


@csrf_exempt
@login_required
def kakao_pay_request(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        user = request.user
        order_id = f"ORDER_{user.id}_{Payment.objects.count() + 1}"
        
        headers = {
            "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        
        data = {
            "cid": "TC0ONETIME",  # 테스트용 CID
            "partner_order_id": order_id,
            "partner_user_id": user.username,
            "item_name": "Test Item",
            "quantity": 1,
            "total_amount": amount,
            "vat_amount": int(int(amount) * 0.1),
            "tax_free_amount": 0,
            "approval_url": request.build_absolute_uri("/pay/kakao/pay/success"),
            "cancel_url": request.build_absolute_uri("/pay/kakao/pay/cancel"),
            "fail_url": request.build_absolute_uri("/pay/kakao/pay/fail"),
        }

        response = requests.post(KAKAO_PAY_URL, headers=headers, data=data)

        if response.status_code == 200:
            result = response.json()
            request.session['tid'] = result['tid']  # Transaction ID 저장
            Payment.objects.create(
                user=user,
                order_id=order_id,
                amount=amount,
                payment_status="pending",
            )
            return redirect(result["next_redirect_pc_url"])
        else:
            return JsonResponse({"error": "카카오페이 요청 실패", "details": response.json()})

    return render(request, "pay/payment_request.html")


@login_required
def kakao_pay_approve(request):
    tid = request.session.get('tid')
    pg_token = request.GET.get('pg_token')

    url = "https://kapi.kakao.com/v1/payment/approve"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "cid": "TC0ONETIME",
        "tid": tid,
        "partner_order_id": "1001",
        "partner_user_id": request.user.username,
        "pg_token": pg_token,
    }

    response = requests.post(url, headers=headers, data=data)
    res_json = response.json()

    if response.status_code == 200:
        payment = Payment.objects.get(order_id="1001")  # 예시로 사용된 주문 ID
        payment.payment_status = "approved"
        payment.save()

        #결제 완료시 장바구니 비우기
        cart = Cart.objects.get(cart_id=_cart_id(request))
        CartItem.objects.filter(cart=cart).delete()

        return JsonResponse(res_json)
    else:
        return JsonResponse({"error": res_json})


@login_required
def kakao_pay_cancel(request):
    return render(request, "payment_cancel.html")


@login_required
def kakao_pay_fail(request):
    return render(request, "payment_fail.html")

def payment_page(request):
    return render(request, "pay/payment_page.html") 
