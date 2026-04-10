from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .models import Profile, Message
from category.models import Favorite, CartItem, Order
from django.db.models import Sum


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome! Login successful.')
            return redirect('all-cats')
        error = 'Invalid username or password.'
    return render(request, 'app/login.html', {'error': error})


def home_view(request):
    from category.models import SubCategory
    from category.models import Favorite
    from django.contrib.auth.models import User
    from .models import HomeContent, HomeSection
    home_content, _ = HomeContent.objects.get_or_create(id=1)
    sections = HomeSection.objects.all().order_by('created_at')

    # Home 12 cards follow the SAME order as a single curator account's Favorites
    # so guest + logged-in users see the same order.
    # Prefer the 'admin' superuser as curator; fallback to first superuser, else first staff.
    curator = (User.objects.filter(is_superuser=True, username='admin').first()
               or User.objects.filter(is_superuser=True).order_by('id').first()
               or User.objects.filter(is_staff=True).order_by('id').first())

    staff_product_ids = []
    fav_map = {}
    if curator:
        curator_favs = list(
            Favorite.objects
            .filter(user=curator)
            .order_by('sort_order', 'id')[:12]
        )
        staff_product_ids = [f.product_id for f in curator_favs]
        fav_map = {f.product_id: f.id for f in curator_favs}

    # Fetch products and keep the same order as ids.
    staff_products = list(SubCategory.objects.filter(id__in=staff_product_ids))
    by_id = {p.id: p for p in staff_products}
    ordered_products = [by_id[pid] for pid in staff_product_ids if pid in by_id]

    # If fewer than 12, fill with newest products (excluding already included).
    if len(ordered_products) < 12:
        need = 12 - len(ordered_products)
        fill_qs = (SubCategory.objects
                   .exclude(id__in=[p.id for p in ordered_products])
                   .order_by('-id')[:need])
        ordered_products.extend(list(fill_qs))

    home_products = ordered_products[:12]
    best_sellers = home_products[:6]
    recommended = home_products[6:12]

    home_pairs = [{'product': p, 'fav_id': fav_map.get(p.id)} for p in home_products]
    return render(request, 'app/home.html', {
        'home_pairs': home_pairs,
        'best_sellers': best_sellers,
        'recommended': recommended,
        # Admin + staff can reorder; everyone sees the same site-wide order.
        'can_reorder_home': bool(request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)),
        'home_content': home_content,
        'sections': sections,
    })


@login_required(login_url='login')
def home_reorder(request):
    # Admin + staff can reorder home cards (site-wide order stored on curator favorites).
    from django.contrib.auth.models import User
    curator = (User.objects.filter(is_superuser=True, username='admin').first()
               or User.objects.filter(is_superuser=True).order_by('id').first())
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff) and curator):
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

    from category.models import Favorite
    favs = list(Favorite.objects.filter(user=curator, id__in=ids))
    by_id = {f.id: f for f in favs}
    ordered = [by_id[i] for i in ids if i in by_id]

    from django.db import transaction
    with transaction.atomic():
        for idx, f in enumerate(ordered):
            Favorite.objects.filter(id=f.id, user=curator).update(sort_order=idx)

    from django.http import JsonResponse
    return JsonResponse({'ok': True})


def landing_view(request):
    from .models import LandingContent
    landing, _ = LandingContent.objects.get_or_create(id=1)
    return render(request, 'app/landing.html', {'hide_top_nav': True, 'landing': landing})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser, login_url='landing')
def landing_edit_view(request):
    from .models import LandingContent
    landing, _ = LandingContent.objects.get_or_create(id=1)
    if request.method == 'POST':
        landing.hero_title = request.POST.get('hero_title', '').strip()
        landing.hero_subtitle = request.POST.get('hero_subtitle', '').strip()
        landing.trust_line = request.POST.get('trust_line', '').strip()
        landing.about_text = request.POST.get('about_text', '').strip()
        landing.mission_text = request.POST.get('mission_text', '').strip()
        landing.vision_text = request.POST.get('vision_text', '').strip()
        landing.services_text = request.POST.get('services_text', '').strip()
        landing.projects_1 = request.POST.get('projects_1', '').strip()
        landing.projects_2 = request.POST.get('projects_2', '').strip()
        landing.projects_3 = request.POST.get('projects_3', '').strip()
        landing.activities_1 = request.POST.get('activities_1', '').strip()
        landing.activities_2 = request.POST.get('activities_2', '').strip()
        landing.activities_3 = request.POST.get('activities_3', '').strip()
        landing.testimonial_1 = request.POST.get('testimonial_1', '').strip()
        landing.testimonial_2 = request.POST.get('testimonial_2', '').strip()
        landing.testimonial_3 = request.POST.get('testimonial_3', '').strip()
        landing.partner_1 = request.POST.get('partner_1', '').strip()
        landing.partner_2 = request.POST.get('partner_2', '').strip()
        landing.partner_3 = request.POST.get('partner_3', '').strip()
        landing.partner_4 = request.POST.get('partner_4', '').strip()
        landing.faq1_q = request.POST.get('faq1_q', '').strip()
        landing.faq1_a = request.POST.get('faq1_a', '').strip()
        landing.faq2_q = request.POST.get('faq2_q', '').strip()
        landing.faq2_a = request.POST.get('faq2_a', '').strip()
        landing.newsletter_text = request.POST.get('newsletter_text', '').strip()
        landing.contact_phone = request.POST.get('contact_phone', '').strip()
        landing.contact_email = request.POST.get('contact_email', '').strip()
        landing.contact_address = request.POST.get('contact_address', '').strip()
        landing.careers_text = request.POST.get('careers_text', '').strip()
        landing.cta_title = request.POST.get('cta_title', '').strip()
        landing.cta_button_text = request.POST.get('cta_button_text', '').strip()
        landing.save()
        messages.success(request, 'Landing updated.')
        return redirect('landing')
    return render(request, 'app/landing_edit.html', {'landing': landing, 'hide_top_nav': True})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser, login_url='home')
def home_edit_view(request):
    from .models import HomeContent, HomeSection
    from category.models import SubCategory
    home_content, _ = HomeContent.objects.get_or_create(id=1)
    if request.method == 'POST':
        if request.POST.get('action') == 'add_section':
            product_id = request.POST.get('section_product')
            subtitle = request.POST.get('section_subtitle', '').strip()
            if product_id:
                try:
                    product = SubCategory.objects.get(id=product_id)
                    HomeSection.objects.create(title=product.name, subtitle=subtitle, product=product)
                except SubCategory.DoesNotExist:
                    pass
            return redirect('home-edit')

        home_content.video_url = request.POST.get('video_url', '').strip()
        home_content.photo_1 = request.POST.get('photo_1', '').strip()
        home_content.photo_2 = request.POST.get('photo_2', '').strip()
        home_content.photo_3 = request.POST.get('photo_3', '').strip()
        if request.FILES.get('hero_photo_1'):
            home_content.hero_photo_1 = request.FILES.get('hero_photo_1')
        if request.FILES.get('hero_photo_2'):
            home_content.hero_photo_2 = request.FILES.get('hero_photo_2')
        if request.FILES.get('hero_photo_3'):
            home_content.hero_photo_3 = request.FILES.get('hero_photo_3')
        home_content.save()
        messages.success(request, 'Home updated.')
        return redirect('home')
    sections = HomeSection.objects.all().order_by('-created_at')
    products = SubCategory.objects.all().order_by('name')
    return render(request, 'app/home_edit.html', {
        'home_content': home_content,
        'sections': sections,
        'products': products,
        'hide_top_nav': True,
    })


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser, login_url='home')
def home_section_delete(request, section_id):
    from .models import HomeSection
    section = get_object_or_404(HomeSection, id=section_id)
    section.delete()
    return redirect('home-edit')


def register_view(request):
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if password != password2:
            error = 'Passwords do not match.'
        elif not username or not password:
            error = 'Please fill required fields.'
        elif User.objects.filter(username=username).exists():
            error = 'Username already exists.'
        else:
            user = User.objects.create_user(username=username, password=password)
            if name:
                user.first_name = name
                user.save()
            customer_group, _ = Group.objects.get_or_create(name='customer')
            user.groups.add(customer_group)
            login(request, user)
            messages.success(request, 'Welcome! Your account is ready.')
            return redirect('all-cats')

    return render(request, 'app/register.html', {'error': error})


@login_required(login_url='login')
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    favorites_count = Favorite.objects.filter(user=request.user).count()
    cart_count = CartItem.objects.filter(user=request.user).count()
    orders_count = Order.objects.filter(user=request.user).count()
    total_spent = Order.objects.filter(user=request.user).aggregate(s=Sum('total'))['s'] or 0
    messages_count = Message.objects.filter(user=request.user).count()
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    context = {
        'profile': profile,
        'favorites_count': favorites_count,
        'cart_count': cart_count,
        'orders_count': orders_count,
        'total_spent': total_spent,
        'messages_count': messages_count,
        'recent_orders': recent_orders,
        'hide_top_nav': True,
    }
    if request.user.is_superuser:
        cutoff = timezone.now() - timedelta(days=30)
        total_users = User.objects.count()
        active_users = User.objects.filter(last_login__gte=cutoff).count()
        never_logged_in = User.objects.filter(last_login__isnull=True).count()
        inactive_users = total_users - active_users
        staff_count = User.objects.filter(is_staff=True).count()
        total_hearts = Favorite.objects.count()
        active_hearts = Favorite.objects.values('user').distinct().count()
        context.update({
            'admin_total_users': total_users,
            'admin_active_users': active_users,
            'admin_inactive_users': inactive_users,
            'admin_never_logged_in': never_logged_in,
            'admin_staff_count': staff_count,
            'admin_total_hearts': total_hearts,
            'admin_active_hearts': active_hearts,
        })
    return render(request, 'app/profile.html', context)


@login_required(login_url='login')
def profile_edit_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    error = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if username and User.objects.exclude(id=request.user.id).filter(username=username).exists():
            error = 'Username already exists.'
        else:
            if name:
                request.user.first_name = name
            if username:
                request.user.username = username
            request.user.save()

            profile.phone = phone
            profile.address = address
            profile.save()

            messages.success(request, 'Profile updated.')
            return redirect('profile')

    context = {
        'profile': profile,
        'error': error,
    }
    return render(request, 'app/profile_edit.html', context)


@login_required(login_url='login')
@login_required(login_url='login')
@login_required(login_url='login')
def messages_view(request):
    user = request.user
    context = {}

    profile, _ = Profile.objects.get_or_create(user=user)
    profile.last_message_read_at = timezone.now()
    profile.save(update_fields=['last_message_read_at'])

    if user.is_staff or user.is_superuser:
        channel = request.GET.get('channel', 'support')
        if channel == 'staff_admin':
            context['channel'] = 'staff_admin'
            context['thread'] = Message.objects.filter(channel='staff_admin').order_by('created_at')
            context['is_staff_view'] = True
        else:
            customer_id = request.GET.get('customer')
            if user.is_superuser:
                from django.contrib.auth.models import User
                customers = User.objects.filter(is_staff=False, is_superuser=False).values('id', 'username')
                customer_threads = []
                for c in customers:
                    last_msg = (Message.objects.filter(channel='support', customer_id=c['id'])
                                .order_by('-created_at')
                                .first())
                    customer_threads.append({
                        'id': c['id'],
                        'username': c['username'],
                        'last_text': last_msg.text if last_msg else '',
                        'last_time': last_msg.created_at if last_msg else None,
                    })
            else:
                customers = (Message.objects.filter(channel='support')
                             .exclude(customer=None)
                             .values('customer_id', 'customer__username')
                             .distinct())
                customer_threads = []
                for c in customers:
                    last_msg = (Message.objects.filter(channel='support', customer_id=c['customer_id'])
                                .order_by('-created_at')
                                .first())
                    customer_threads.append({
                        'id': c['customer_id'],
                        'username': c['customer__username'],
                        'last_text': last_msg.text if last_msg else '',
                        'last_time': last_msg.created_at if last_msg else None,
                    })
            context['customers'] = customer_threads
            if (not customer_id) and customer_threads:
                customer_id = customer_threads[0]['id']
            context['customer_id'] = customer_id
            context['channel'] = 'support'
            if customer_id:
                thread = Message.objects.filter(channel='support', customer_id=customer_id).order_by('created_at')
            else:
                thread = Message.objects.none()
            context['thread'] = thread
            context['is_staff_view'] = True
    else:
        context['channel'] = 'support'
        context['customer_id'] = user.id
        thread = Message.objects.filter(channel='support', customer=user).order_by('created_at')
        context['thread'] = thread
        context['is_staff_view'] = False

    return render(request, 'app/messages.html', context)


@login_required(login_url='login')
def message_center_view(request):
    user = request.user
    context = {}
    if user.is_staff or user.is_superuser:
        if user.is_superuser:
            from django.contrib.auth.models import User
            customers = User.objects.filter(is_staff=False, is_superuser=False).values('id', 'username')
            customer_threads = []
            for c in customers:
                last_msg = (Message.objects.filter(channel='support', customer_id=c['id'])
                            .order_by('-created_at')
                            .first())
                customer_threads.append({
                    'id': c['id'],
                    'username': c['username'],
                    'last_text': last_msg.text if last_msg else '',
                    'last_time': last_msg.created_at if last_msg else None,
                })
        else:
            customers = (Message.objects.filter(channel='support')
                         .exclude(customer=None)
                         .values('customer_id', 'customer__username')
                         .distinct())
            customer_threads = []
            for c in customers:
                last_msg = (Message.objects.filter(channel='support', customer_id=c['customer_id'])
                            .order_by('-created_at')
                            .first())
                customer_threads.append({
                    'id': c['customer_id'],
                    'username': c['customer__username'],
                    'last_text': last_msg.text if last_msg else '',
                    'last_time': last_msg.created_at if last_msg else None,
                })
        context['customers'] = customer_threads
        context['show_staff_admin'] = True
    else:
        thread = Message.objects.filter(channel='support', customer=user).order_by('-created_at')[:5]
        context['recent_messages'] = thread
    context['hide_top_nav'] = True
    return render(request, 'app/message_center.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')
