from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Order, OrderItem
from django.db.models import Sum
from datetime import datetime, timedelta




# ---------------- HOME ----------------
def home_view(request):
    category_id = request.GET.get('category')
    categories = Category.objects.all()

    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all().order_by('-created_at')

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
    })


def detail_view(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'detail.html', {'product': product})


# ---------------- CART ----------------
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)

    quantity = int(request.POST.get('quantity', 1))
    current_qty = cart.get(str(product_id), 0)

    if current_qty + quantity > product.quantity:
        cart[str(product_id)] = product.quantity
    else:
        cart[str(product_id)] = current_qty + quantity

    request.session['cart'] = cart
    return redirect('cart')


def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        total_price = product.price * quantity

        items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_price
        })

        total += total_price

    return render(request, 'cart.html', {'items': items, 'total': total})


def remove_item(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart')


def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart')


def update_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)

    action = request.POST.get('action')

    if str(product_id) in cart:
        if action == 'plus' and cart[str(product_id)] < product.quantity:
            cart[str(product_id)] += 1
        elif action == 'minus' and cart[str(product_id)] > 1:
            cart[str(product_id)] -= 1

    request.session['cart'] = cart
    return redirect('cart')


def cart_count(request):
    cart = request.session.get('cart', {})
    return {'cart_count': sum(cart.values())}


# ---------------- CHECKOUT ----------------
def checkout_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        total_price = product.price * quantity

        items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_price
        })

        total += total_price

    return render(request, 'checkout.html', {'items': items, 'total': total})


# 🔥🔥🔥 ГЛАВНЫЙ ФИКС
def create_order(request):
    if request.method == "POST":
        cart = request.session.get('cart', {})

        if not cart:
            return redirect('home')

        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        comment = request.POST.get('comment')

        order = Order.objects.create(
            name=name,
            phone=phone,
            address=address,
            comment=comment,
            total_price=0
        )

        total = 0

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            total_price = product.price * quantity

            # 🔥 СОЗДАЕМ СВЯЗЬ С ORDER
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                total_price=total_price
            )

            total += total_price

        order.total_price = total
        order.save()

        request.session['cart'] = {}

        return redirect('success', order_code=order.order_code)


def success_view(request, order_code):
    return render(request, 'success.html', {'order_code': order_code})


# ---------------- ADMIN ----------------

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "admin" and password == "1234":
            request.session["is_admin"] = True
            return redirect("dashboard")

    return render(request, "admin_login.html")


def admin_logout(request):
    request.session.flush()
    return redirect("home")


def dashboard(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")

    orders = Order.objects.all().order_by('-created_at')

    total_money = sum(o.total_price for o in orders)

    labels = []
    data = []

    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)
        day_orders = Order.objects.filter(created_at__date=day.date())
        day_total = sum(o.total_price for o in day_orders)

        labels.append(day.strftime("%d-%m"))
        data.append(day_total)

    top_products = (
        OrderItem.objects
        .values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    return render(request, "dashboard.html", {
        "orders": orders,
        "orders_count": orders.count(),
        "total_money": total_money,
        "labels": labels,
        "data": data,
        "top_products": top_products
    })


# ---------------- BUYURTMALAR ----------------

def orders_view(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")

    orders = Order.objects.all().order_by('-created_at')

    return render(request, "orders.html", {
        "orders": orders
    })


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()  # 🔥 ВОТ ЭТО ОБЯЗАТЕЛЬНО

    return render(request, "order_detail.html", {
        "order": order,
        "items": items
    })




def change_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)

        status = request.POST.get("status")

        if status in ['pending', 'ready', 'delivered', 'cancelled']:
            order.status = status
            order.save()

    return redirect("order_detail", order_id=order.id)


# ================= MIJOZLAR =================
def customers_view(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")

    orders = Order.objects.all()

    customers = {}

    for order in orders:
        phone = order.phone

        if phone not in customers:
            customers[phone] = {
                "name": order.name,
                "phone": phone,
                "orders": 0,
                "total": 0
            }

        customers[phone]["orders"] += 1
        customers[phone]["total"] += order.total_price

    return render(request, "customers.html", {
        "customers": customers.values()
    })


# ================= PRODUCTS =================
def products_view(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")

    products = Product.objects.all()
    categories = Category.objects.all()

    return render(request, "products.html", {
        "products": products,
        "categories": categories
    })


def delete_product(request, id):
    Product.objects.filter(id=id).delete()
    return redirect("products")


def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.quantity = request.POST.get("quantity")
        product.category_id = request.POST.get("category")
        product.description = request.POST.get("description")
        product.cost = request.POST.get("cost")
        product.type = request.POST.get("type")
        product.image_url = request.POST.get("image_url")

        product.save()
        return redirect("products")

    return render(request, "edit_product.html", {
        "product": product,
        "categories": categories
    })


# ================= CATEGORIES =================
def categories_view(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")

    categories = Category.objects.all()

    return render(request, "categories.html", {
        "categories": categories
    })


def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        Category.objects.create(name=name)

    return redirect("categories")


def edit_category(request, id):
    cat = get_object_or_404(Category, id=id)

    if request.method == "POST":
        cat.name = request.POST.get("name")
        cat.save()

    return redirect("categories")


def delete_category(request, id):
    Category.objects.filter(id=id).delete()
    return redirect("categories")


def categories_view(request):
    categories = Category.objects.all()

    return render(request, "categories.html", {
        "categories": categories
    })


def edit_category(request, category_id):
    if not request.session.get("is_admin"):
        return redirect("admin_login")

    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.name = request.POST.get("name")

        # 🔥 добавили order
        order_value = request.POST.get("order")

        if order_value:
            category.order = int(order_value)

        category.save()
        return redirect("categories")

    return render(request, "edit_category.html", {
        "category": category
    })




def add_product(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")

    categories = Category.objects.all()

    if request.method == "POST":
        Product.objects.create(
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            price=request.POST.get("price"),
            cost=request.POST.get("cost"),
            quantity=request.POST.get("quantity"),
            type=request.POST.get("type"),
            category_id=request.POST.get("category"),
            image_url=request.POST.get("image_url")  # 🔥 ссылка на фото
        )
        return redirect("products")

    return render(request, "add_product.html", {
        "categories": categories
    })

# ================= MOLIYA =================
def finance_view(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")

    orders = Order.objects.all()
    items = OrderItem.objects.all()

    total_income = sum(o.total_price for o in orders)
    total_cost = sum(i.product.cost * i.quantity for i in items)
    profit = total_income - total_cost

    avg_check = total_income // orders.count() if orders.exists() else 0
    profit_percent = round((profit / total_income) * 100, 1) if total_income else 0

    # 📉 тренд (просто пример)
    trend = -98 if profit < total_income else 10

    # 📅 график
    labels = []
    income_data = []
    profit_data = []

    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)

        day_orders = Order.objects.filter(created_at__date=day.date())
        day_items = OrderItem.objects.filter(created_at__date=day.date())

        day_income = sum(o.total_price for o in day_orders)
        day_cost = sum(i.product.cost * i.quantity for i in day_items)

        labels.append(day.strftime("%d-%m"))
        income_data.append(day_income)
        profit_data.append(day_income - day_cost)

    # 🧁 статусы
    pending = Order.objects.filter(status="pending").count()
    ready = Order.objects.filter(status="ready").count()
    delivered = Order.objects.filter(status="delivered").count()

    # 📊 таблица товаров
    product_stats = []

    products = Product.objects.all()

    for p in products:
        product_items = OrderItem.objects.filter(product=p)

        total_qty = sum(i.quantity for i in product_items)
        total_income_p = sum(i.total_price for i in product_items)
        total_cost_p = p.cost * total_qty
        profit_p = total_income_p - total_cost_p

        margin = round((profit_p / total_income_p) * 100, 1) if total_income_p else 0

        product_stats.append({
            "name": p.name,
            "qty": total_qty,
            "income": total_income_p,
            "profit": profit_p,
            "margin": margin
        })

    product_stats = sorted(product_stats, key=lambda x: x["income"], reverse=True)

    # 📊 bar chart
    bar_labels = [p["name"] for p in product_stats[:5]]
    bar_income = [p["income"] for p in product_stats[:5]]

    return render(request, "finance.html", {
        "total_income": total_income,
        "total_cost": total_cost,
        "profit": profit,
        "avg_check": avg_check,
        "profit_percent": profit_percent,
        "trend": trend,
        "orders_count": orders.count(),

        "labels": labels,
        "income_data": income_data,
        "profit_data": profit_data,

        "pending": pending,
        "ready": ready,
        "delivered": delivered,

        "product_stats": product_stats,

        "bar_labels": bar_labels,
        "bar_income": bar_income
    })