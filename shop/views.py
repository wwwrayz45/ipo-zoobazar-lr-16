
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import Product, Cart, CartItem


def home(request):
    return HttpResponse("""
    <h1>Zoobazar</h1>
    <a href="/author/">Об авторе</a><br>
    <a href="/shop/">О магазине</a>
    """)


def author(request):
    return HttpResponse("""
    Автор лабораторной работы: Будько Дарья<br>
    Учебная группа: 87 ТП
    """)


def shop_info(request):
    return HttpResponse("""
    <h2>О магазине Zoobazar</h2>
    <p>Zoobazar — сеть зоомагазинов в Беларуси.</p>
    """)


from django.http import HttpResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import Product, Cart, CartItem


def home(request):
    return HttpResponse("""
    <h1>Zoobazar</h1>
    <a href="/author/">Об авторе</a><br>
    <a href="/shop/">О магазине</a>
    """)


def author(request):
    return HttpResponse("""
    Автор лабораторной работы: Будько Дарья<br>
    Учебная группа: 87 ТП
    """)


def shop_info(request):
    return HttpResponse("""
    <h2>О магазине Zoobazar</h2>
    <p>Zoobazar — сеть зоомагазинов в Беларуси.</p>
    """)


def product_list(request):
    products = Product.objects.all()

    category = request.GET.get("category")
    manufacturer = request.GET.get("manufacturer")
    search = request.GET.get("search")

    if category:
        products = products.filter(category_id=category)

    if manufacturer:
        products = products.filter(manufacturer_id=manufacturer)

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    return render(
        request,
        "shop/product_list.html",
        {"products": products}
    )


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return render(
        request,
        "shop/product_detail.html",
        {"product": product}
    )


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    items = cart.cartitem_set.all()

    total = sum(
        item.item_price()
        for item in items
    )

    return render(
        request,
        "shop/cart.html",
        {
            "items": items,
            "total": total
        }
    )


def add_to_cart(request, product_id):
    return HttpResponse(f"Товар {product_id} добавлен в корзину")


def update_cart_item(request, item_id):
    return HttpResponse(f"Количество товара {item_id} обновлено")


def remove_from_cart(request, item_id):
    return HttpResponse(f"Товар {item_id} удалён из корзины")


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return HttpResponse(f"""
    <h2>{product.name}</h2>
    <p>{product.description}</p>
    <p>Цена: {product.price}</p>
    <p>На складе: {product.stock_quantity}</p>
    """)


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    result = "<h2>Корзина</h2>"
    total = 0

    for item in cart.cartitem_set.all():
        cost = item.item_price()

        result += (
            f"{item.product.name} "
            f"({item.quantity} шт.) "
            f"= {cost}<br>"
        )

        total += cost

    result += f"<h3>Общая стоимость: {total}</h3>"

    return HttpResponse(result)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        item.quantity += 1
        item.save()

    return HttpResponse("Товар добавлен в корзину")


@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(
        CartItem,
        pk=item_id,
        cart__user=request.user
    )

    quantity = int(request.GET.get('quantity', 1))

    if quantity > item.product.stock_quantity:
        return HttpResponse(
            "Количество превышает остаток на складе"
        )

    item.quantity = quantity
    item.save()

    return HttpResponse("Количество обновлено")


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        pk=item_id,
        cart__user=request.user
    )

    item.delete()

    return HttpResponse("Товар удалён из корзины")