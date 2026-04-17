from django.core.cache import cache
from .models import LandingContent, Message, Profile
from category.models import CartItem

def branding(request):
    landing = cache.get('landing_content')
    if not landing:
        landing, _ = LandingContent.objects.get_or_create(id=1)
        cache.set('landing_content', landing, timeout=60 * 60 * 24) # Cache for 24 hours
    return {'landing': landing}

def user_role(request):
    role = None
    if request.user.is_authenticated:
        if request.user.is_superuser:
            role = 'admin'
        elif request.user.is_staff:
            role = 'staff'
        else:
            role = 'customer'
    return {'user_role': role}

def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    return {'cart_count': count}

def chat_unread_count(request):
    count = 0
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            # ဝန်ထမ်းများအတွက်: Customer များဆီမှလာပြီး မဖတ်ရသေးသော စာများ
            count = Message.objects.filter(is_staff_response=False, is_read=False).count()
        else:
            # Customer များအတွက်: မိမိဆီသို့ ဝန်ထမ်းမှပို့ထားပြီး မဖတ်ရသေးသော စာများ
            count = Message.objects.filter(customer=request.user, is_staff_response=True, is_read=False).count()
    return {'chat_unread_count': count}