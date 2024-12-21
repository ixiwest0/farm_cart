from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Order
from .forms import ProductForm
from django.db.models import Sum 


@login_required
def dashboard(request):
    # 판매자의 데이터를 가져옴
    total_sales = Product.objects.filter(seller=request.user).aggregate(total_sales=Sum('sales'))['total_sales'] or 0
    total_orders = Order.objects.filter(product__seller=request.user).count()
    total_revenue = Order.objects.filter(product__seller=request.user).aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0
    
    return render(request, 'seller/dashboard.html', {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
    })

@login_required
def product_list(request):
    # 로그인한 판매자의 상품 목록
    products = Product.objects.filter(seller=request.user)
    return render(request, 'seller/product_list.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user  # 현재 판매자로 지정
            product.save()
            return redirect('seller:product_list')
    else:
        form = ProductForm()
    return render(request, 'seller/add_product.html', {'form': form})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'seller/add_product.html', {'form': form})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('seller:product_list')
    return render(request, 'seller/product_confirm_delete.html', {'product': product})

@login_required
def order_list(request):
    # 로그인한 판매자의 주문 목록
    orders = Order.objects.filter(product__seller=request.user)
    return render(request, 'seller/order_list.html', {'orders': orders})
