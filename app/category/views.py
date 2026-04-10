from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from .models import Category, SubCategory 
from .models import Favorite, CartItem, Order, OrderItem

def _to_float(value, default):
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def _to_int(value, default):
    if value is None or value == '':
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def cats(request):
    sort = request.GET.get('sort', '')
    cats_qs = Category.objects.all()
    if sort == 'name_asc':
        cats_qs = cats_qs.order_by('name')
    elif sort == 'name_desc':
        cats_qs = cats_qs.order_by('-name')
    elif sort == 'newest':
        cats_qs = cats_qs.order_by('-id')
    else:
        cats_qs = cats_qs.order_by('sort_order', 'id')
    context = {
        'cats': cats_qs,
        'sort': sort,
        'can_reorder_cats': bool(request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser) and sort == ''),
    }
    return render(request, 'category/cats.html', context)


@login_required(login_url='login')
def cats_reorder(request):
    if not (request.user.is_staff or request.user.is_superuser):
        from django.http import JsonResponse
        return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)
    if request.method != 'POST':
        from django.http import JsonResponse
        return JsonResponse({'ok': False, 'error': 'method_not_allowed'}, status=405)

    try:
        import json
        payload = json.loads(request.body.decode('utf-8') or '{}')
        ids = payload.get('ids') or []
        ids = [int(x) for x in ids]
    except Exception:
        from django.http import JsonResponse
        return JsonResponse({'ok': False, 'error': 'invalid_payload'}, status=400)

    cats_list = list(Category.objects.filter(id__in=ids))
    by_id = {c.id: c for c in cats_list}
    ordered = [by_id[i] for i in ids if i in by_id]

    from django.db import transaction
    with transaction.atomic():
        for idx, c in enumerate(ordered):
            Category.objects.filter(id=c.id).update(sort_order=idx)

    from django.http import JsonResponse
    return JsonResponse({'ok': True})

@staff_member_required(login_url='login')
def cat_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        image = request.FILES.get('image')
        if name and image:
            Category.objects.create(name=name, image=image)
            return redirect('all-cats')
    return render(request, 'category/cat_create.html')

@login_required(login_url='login')
@staff_member_required(login_url='login')
def cat_edit_list(request):
    cats_qs = Category.objects.all()
    return render(request, 'category/cat_edit_list.html', {'cats': cats_qs})


@login_required(login_url='login')
@staff_member_required(login_url='login')
def cat_edit(request, cat_id):
    cat = get_object_or_404(Category, id=cat_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        image = request.FILES.get('image')
        if name:
            cat.name = name
        if image:
            cat.image = image
        cat.save()
        return redirect('cat-edit-list')
    return render(request, 'category/cat_edit.html', {'cat': cat})


def cat_products(request, cat_id):
    cat = get_object_or_404(Category, id=cat_id)
    products = SubCategory.objects.filter(parent=cat)
    context = {
        'cat': cat,
        'products': products,
    }
    return render(request, 'category/cat_products.html', context)

def subs(request):
    sort = request.GET.get('sort', '')
    subs_qs = SubCategory.objects.all()
    if sort == 'name_asc':
        subs_qs = subs_qs.order_by('name')
    elif sort == 'name_desc':
        subs_qs = subs_qs.order_by('-name')
    elif sort == 'price_asc':
        subs_qs = subs_qs.order_by('price')
    elif sort == 'price_desc':
        subs_qs = subs_qs.order_by('-price')
    elif sort == 'newest':
        subs_qs = subs_qs.order_by('-id')
    return render(request, 'category/subs.html', {'subs': subs_qs, 'sort': sort})

def sub_detail(request, sub_id):
    sub = get_object_or_404(SubCategory, id=sub_id)
    related = SubCategory.objects.filter(parent=sub.parent).exclude(id=sub.id)[:6]
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, product=sub).exists()
    return render(request, 'category/sub_detail.html', {
        'sub': sub,
        'related': related,
        'is_favorited': is_favorited,
        'hide_top_nav': True,
    })


@login_required(login_url='login')
def toggle_favorite(request, sub_id):
    sub = get_object_or_404(SubCategory, id=sub_id)
    fav = Favorite.objects.filter(user=request.user, product=sub).first()
    if fav:
        fav.delete()
    else:
        # New rule: staff can only keep 12 hearts.
        # If they heart a 13th product, auto-remove the oldest heart and add the new one.
        if request.user.is_staff:
            staff_favs = Favorite.objects.filter(user=request.user).order_by('id')
            if staff_favs.count() >= 12:
                oldest = staff_favs.first()
                if oldest:
                    oldest.delete()
                from django.contrib import messages
                messages.info(request, 'Replaced the oldest staff heart to keep only 12 products.')
        next_order = (Favorite.objects.filter(user=request.user).aggregate(m=models.Max('sort_order'))['m'] or 0) + 1
        Favorite.objects.create(user=request.user, product=sub, sort_order=next_order)
    return redirect('sub-detail', sub_id=sub.id)

def toggle_favorite_guest(request, sub_id):
    from django.contrib import messages
    messages.info(request, 'Please login to add favorites.')
    return redirect(f"/login/?next=/cats/subs/{sub_id}/")


@login_required(login_url='login')
def favorites(request):
    favs = (Favorite.objects
            .filter(user=request.user)
            .select_related('product')
            .order_by('sort_order', 'id'))

    top_ten = []
    if request.user.is_superuser:
        from django.db.models import Count
        from .models import SubCategory
        top_ids = list(
            Favorite.objects
            .filter(user__is_staff=False, user__is_superuser=False)
            .values('product_id')
            .annotate(c=Count('id'))
            .order_by('-c')[:10]
        )
        ids = [x['product_id'] for x in top_ids]
        counts = {x['product_id']: x['c'] for x in top_ids}
        products = list(SubCategory.objects.filter(id__in=ids))
        by_id = {p.id: p for p in products}
        top_ten = [{'product': by_id[i], 'count': counts.get(i, 0)} for i in ids if i in by_id]

    return render(request, 'category/favorites.html', {'favs': favs, 'top_ten': top_ten})


@login_required(login_url='login')
def favorites_reorder(request):
    if request.method != 'POST':
        return redirect('favorites')
    try:
        import json
        payload = json.loads(request.body.decode('utf-8') or '{}')
        ids = payload.get('ids') or []
        ids = [int(x) for x in ids]
    except Exception:
        from django.http import JsonResponse
        return JsonResponse({'ok': False, 'error': 'invalid_payload'}, status=400)

    # Only reorder favorites belonging to this user
    favs = list(Favorite.objects.filter(user=request.user, id__in=ids))
    by_id = {f.id: f for f in favs}

    ordered = [by_id[i] for i in ids if i in by_id]
    from django.db import transaction
    with transaction.atomic():
        for idx, f in enumerate(ordered):
            Favorite.objects.filter(id=f.id, user=request.user).update(sort_order=idx)

    from django.http import JsonResponse
    return JsonResponse({'ok': True})


@login_required(login_url='login')
def add_to_cart(request, sub_id):
    sub = get_object_or_404(SubCategory, id=sub_id)
    item = CartItem.objects.filter(user=request.user, product=sub).first()
    if item:
        item.quantity += 1
        item.save()
    else:
        CartItem.objects.create(user=request.user, product=sub, quantity=1)
    from django.contrib import messages
    messages.success(request, 'Added to cart.')
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('sub-detail', sub_id=sub.id)

def add_to_cart_guest(request, sub_id):
    from django.contrib import messages
    messages.info(request, 'Please login to add items to cart.')
    return redirect(f"/login/?next=/cats/subs/{sub_id}/")

@login_required(login_url='login')
def buy_now(request, sub_id):
    sub = get_object_or_404(SubCategory, id=sub_id)
    item = CartItem.objects.filter(user=request.user, product=sub).first()
    if item:
        item.quantity += 1
        item.save()
    else:
        CartItem.objects.create(user=request.user, product=sub, quantity=1)
    from django.contrib import messages
    messages.success(request, 'Added to cart.')
    return redirect('cart')

def buy_now_guest(request, sub_id):
    from django.contrib import messages
    messages.info(request, 'Please login to buy now.')
    return redirect(f"/login/?next=/cats/subs/{sub_id}/")


@login_required(login_url='login')
def cart_view(request):
    # Staff/admin should not order; they manage customer orders here.
    if request.user.is_staff or request.user.is_superuser:
        orders = (Order.objects
                  .select_related('user')
                  .prefetch_related('items__product')
                  .exclude(user__is_staff=True)
                  .exclude(user__is_superuser=True)
                  .order_by('-created_at'))
        return render(request, 'category/cart.html', {
            'is_staff_view': True,
            'orders': orders,
            'hide_top_nav': True,
        })

    items = CartItem.objects.filter(user=request.user).select_related('product')
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    total = sum((i.product.price * i.quantity) for i in items)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        screenshot = request.FILES.get('kpay_screenshot')

        if payment_method in ('cod', 'kpay') and items.exists():
            if payment_method == 'kpay' and not screenshot:
                return render(request, 'category/cart.html', {
                    'items': items,
                    'total': total,
                    'recent_orders': recent_orders,
                    'error': 'Please upload KPay screenshot.',
                })

            order = Order.objects.create(
                user=request.user,
                total=total,
                payment_method=payment_method,
                kpay_screenshot=screenshot if payment_method == 'kpay' else None,
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )
            items.delete()
            from django.contrib import messages
            messages.success(request, 'Order submitted.')
            return redirect('cart')

    return render(request, 'category/cart.html', {
        'items': items,
        'total': total,
        'recent_orders': recent_orders,
    })


@login_required(login_url='login')
def order_update_status(request, order_id, status):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('cart')
    if request.method != 'POST':
        return redirect('cart')

    allowed = {'accepted', 'delivered', 'cancelled'}
    if status not in allowed:
        return redirect('cart')

    order = get_object_or_404(Order, id=order_id)
    # Do not allow staff/admin orders to be managed here.
    if order.user.is_staff or order.user.is_superuser:
        return redirect('cart')

    # Enforce meaning/workflow:
    # - pending -> accepted OR cancelled
    # - accepted -> delivered OR cancelled
    # - delivered/cancelled are terminal
    current = order.status or 'pending'
    allowed_transitions = {
        'pending': {'accepted', 'cancelled'},
        'accepted': {'delivered', 'cancelled'},
        'delivered': set(),
        'cancelled': set(),
    }
    if status not in allowed_transitions.get(current, set()):
        from django.contrib import messages
        messages.info(request, f'Cannot change status from {current} to {status}.')
        return redirect('cart')

    order.status = status
    order.save(update_fields=['status'])
    from django.contrib import messages
    messages.success(request, f'Order #{order.id} marked as {status}.')
    return redirect('cart')


@login_required(login_url='login')
def update_cart(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if action == 'inc':
        item.quantity += 1
        item.save()
    elif action == 'dec':
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
        else:
            item.save()
    return redirect('cart')

@staff_member_required(login_url='login')
def create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        parent_id = request.POST.get('parent')
        image = request.FILES.get('image')
        details = request.POST.get('details', '').strip()
        color = request.POST.get('color', '').strip()
        size = request.POST.get('size', '').strip()
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price')
        stock = request.POST.get('stock')

        if name and parent_id and image:
            try:
                parent = Category.objects.get(id=parent_id)
                SubCategory.objects.create(
                    name=name,
                    image=image,
                    parent=parent,
                    details=details,
                    color=color,
                    size=size,
                    price=price or 0,
                    discount_price=discount_price or 0,
                    stock=stock or 0,
                )
                return redirect('all-sub-cats')
            except Category.DoesNotExist:
                pass

    context = {
        'cats': Category.objects.all(),
    }
    return render(request, 'category/create.html', context)


@login_required(login_url='login')
@staff_member_required(login_url='login')
def sub_edit_list(request):
    subs_qs = SubCategory.objects.select_related('parent').all()
    return render(request, 'category/sub_edit_list.html', {'subs': subs_qs})


@login_required(login_url='login')
@staff_member_required(login_url='login')
def sub_edit(request, sub_id):
    sub = get_object_or_404(SubCategory, id=sub_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        parent_id = request.POST.get('parent')
        image = request.FILES.get('image')
        details = request.POST.get('details', '').strip()
        color = request.POST.get('color', '').strip()
        size = request.POST.get('size', '').strip()
        price = _to_float(request.POST.get('price'), sub.price)
        discount_price = _to_float(request.POST.get('discount_price'), sub.discount_price)
        stock = _to_int(request.POST.get('stock'), sub.stock)

        if name:
            sub.name = name
        if parent_id:
            try:
                sub.parent = Category.objects.get(id=parent_id)
            except Category.DoesNotExist:
                pass
        if image:
            sub.image = image
        sub.details = details
        sub.color = color
        sub.size = size
        sub.price = price
        sub.discount_price = discount_price
        sub.stock = stock
        sub.save()
        return redirect('sub-edit-list')

    context = {
        'sub': sub,
        'cats': Category.objects.all(),
    }
    return render(request, 'category/sub_edit.html', context)
