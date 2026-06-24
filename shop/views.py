from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.mail import EmailMessage
from django.conf import settings

from io import BytesIO
import openpyxl

from .models import Product, Cart, CartItem


# ---------------- HOME ----------------
def home(request):
    return HttpResponse("""
    <h1>Zoobazar</h1>
    <a href="/author/">Об авторе</a><br>
    <a href="/shop/">О магазине</a>
    """)


# ---------------- AUTHOR ----------------
def author(request):
    return HttpResponse("""
    Автор лабораторной работы: Будько Дарья<br>
    Учебная группа: 87 ТП
    """)


# ---------------- SHOP INFO ----------------
def shop_info(request):
    return HttpResponse("""
    <h2>О магазине Zoobazar</h2>
    <p>Zoobazar — сеть зоомагазинов в Беларуси.</p>
    """)


# ---------------- PRODUCTS ----------------
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

    return render(request, "shop/product_list.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return HttpResponse(f"""
    <h2>{product.name}</h2>
    <p>{product.description}</p>
    <p>Цена: {product.price}</p>
    <p>На складе: {product.stock_quantity}</p>
    """)


# ---------------- CART ----------------
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    items = cart.cartitem_set.all()

    result = "<h2>Корзина</h2>"
    total = 0

    for item in items:
        cost = item.item_price()
        result += f"{item.product.name} ({item.quantity}) = {cost}<br>"
        total += cost

    result += f"<h3>Итого: {total}</h3>"

    return HttpResponse(result)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    cart, _ = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 1}
    )

    if not created:
        item.quantity += 1
        item.save()

    return HttpResponse("Товар добавлен")


@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)

    quantity = int(request.GET.get("quantity", 1))

    if quantity > item.product.stock_quantity:
        return HttpResponse("Нет столько товара на складе")

    item.quantity = quantity
    item.save()

    return HttpResponse("Обновлено")


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()

    return HttpResponse("Удалено из корзины")


@login_required
@transaction.atomic
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.cartitem_set.select_related('product').all()

    if request.method == "GET":
        if not items.exists():
            return HttpResponse("Корзина пуста", status=400)
        return render(request, "shop/checkout.html")

    if not items.exists():
        return HttpResponse("Корзина пуста", status=400)

    address = request.POST.get("address")
    comment = request.POST.get("comment")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Чек"

    ws.append(["Товар", "Кол-во", "Цена", "Сумма"])

    total = 0

    for item in items:
        price = item.product.price
        sum_item = price * item.quantity
        total += sum_item

        ws.append([
            item.product.name,
            item.quantity,
            float(price),
            float(sum_item)
        ])

    ws.append([])
    ws.append(["Адрес", address])
    ws.append(["Комментарий", comment])
    ws.append(["ИТОГО", "", "", float(total)])

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    email = EmailMessage(
        subject="Ваш чек заказа",
        body=f"Спасибо за покупку!\nАдрес: {address}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[request.user.email],
    )

    email.attach(
        "receipt.xlsx",
        file_stream.read(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    email.send()

    items.delete()

    return HttpResponse("Заказ оформлен успешно!")