import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Payment
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from cart.views import _cart_id
from django.urls import reverse
from django.contrib import messages

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
            "approval_url": request.build_absolute_uri(reverse("pay:kakao_pay_success")),
            "cancel_url": request.build_absolute_uri(reverse("pay:kakao_pay_cancel")),
            "fail_url": request.build_absolute_uri(reverse("pay:kakao_pay_fail")),
        }

        response = requests.post(KAKAO_PAY_URL, headers=headers, data=data)

        if response.status_code == 200:
            result = response.json()
            # 세션에 Transaction ID와 order_id 저장
            request.session['tid'] = result['tid']
            request.session['order_id'] = order_id

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
    order_id = request.session.get('order_id')  # 세션에서 order_id 가져오기
    pg_token = request.GET.get('pg_token')

    url = "https://kapi.kakao.com/v1/payment/approve"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "cid": "TC0ONETIME",
        "tid": tid,
        "partner_order_id": order_id,  # 세션에서 가져온 order_id 사용
        "partner_user_id": request.user.username,
        "pg_token": pg_token,
    }

    response = requests.post(url, headers=headers, data=data)
    res_json = response.json()

    if response.status_code == 200:
        payment = Payment.objects.get(order_id=order_id)  # 동적으로 order_id 사용
        payment.payment_status = "approved"
        payment.save()

        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)

        for cart_item in cart_items:
            product = cart_item.product
            if product.stock >= cart_item.quantity:
                product.stock -= cart_item.quantity
                product.save()

        # 장바구니 비우기
        cart_items.delete()

        # 성공 메시지 추가
        messages.success(request, "결제가 완료되었습니다.")
        return redirect('/')
    else:
        messages.error(request, "결제에 실패했습니다.")
        return JsonResponse({"error": res_json})


@login_required
def kakao_pay_cancel(request):
    return render(request, "payment_cancel.html")


@login_required
def kakao_pay_fail(request):
    return render(request, "payment_fail.html")


def payment_page(request):
    return render(request, "pay/payment_page.html")
