from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # 메시지 라이브러리 사용
from django.core.exceptions import ObjectDoesNotExist
from blog.models import Post
from .models import Cart, CartItem
from django.contrib import messages  # 메시지 라이브러리 사용
from seller.models import Order


# Helper function to get or create session ID
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# Add product to cart
from django.http import JsonResponse  # 추가

def add_cart(request, product_id):
    product = Post.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity + 1 > product.stock:  # 재고 초과 여부 확인
            messages.error(request, "재고 수량을 초과할 수 없습니다.")  # 에러 메시지 추가
            return redirect('cart:cart_detail')
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        if product.stock < 1:
            messages.error(request, "재고가 부족합니다.")  # 에러 메시지 추가
            return redirect('cart:cart_detail')
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()


    return redirect('cart:cart_detail')

def cart_detail(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass  # If no cart or cart items exist


    return render(request, 'cart/cart.html',dict(cart_items=cart_items,
        total=total,
        counter=counter
    ))

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Post, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart:cart_detail')

def delete_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Post, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.delete()  # 아이템을 완전히 삭제
    except CartItem.DoesNotExist:
        pass
    return redirect('cart:cart_detail')

@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        total = 0
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity

        shipping_fee = 0  # 배송비를 0으로 설정
        grand_total = total + shipping_fee
        if request.method == 'POST':
            shipping_address = request.POST.get('shipping_address')
            shipping_detail = request.POST.get('shipping_detail')

            if not shipping_address:
                messages.error(request, "배송 주소를 입력해 주세요.")
                return redirect('cart:checkout')

            for cart_item in cart_items:
                Order.objects.create(
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    total_price=cart_item.product.price * cart_item.quantity,
                    shipping_address=shipping_address,
                    shipping_detail=shipping_detail,
                )
                # 재고 감소
                product = cart_item.product
                if product.stock >= cart_item.quantity:
                    product.stock -= cart_item.quantity
                    product.save()

                # 장바구니 비우기
            cart_items.delete()

            messages.success(request, "결제가 완료되었습니다.")
            return redirect('seller:dashboard')

    except ObjectDoesNotExist:
        cart_items = None
        total = 0
        grand_total = 0
        shipping_fee = 0

    return render(request, 'cart/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'shipping_fee': shipping_fee,
        'grand_total': grand_total,
    })
