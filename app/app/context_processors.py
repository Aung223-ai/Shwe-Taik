from django.contrib.auth.models import AnonymousUser


def user_role(request):
    user = getattr(request, 'user', AnonymousUser())
    if not user or not user.is_authenticated:
        return {'user_role': 'guest'}
    if user.is_superuser:
        return {'user_role': 'admin'}
    if user.is_staff:
        return {'user_role': 'staff'}
    return {'user_role': 'customer'}


def cart_count(request):
    try:
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            from category.models import CartItem
            return {'cart_count': CartItem.objects.filter(user=user).count()}
    except Exception:
        pass
    return {'cart_count': 0}


def chat_unread_count(request):
    try:
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            from .models import Profile, Message
            profile, _ = Profile.objects.get_or_create(user=user)
            last_read = profile.last_message_read_at
            if user.is_staff or user.is_superuser:
                count = Message.objects.filter(
                    channel='support',
                    is_staff_response=False,
                    created_at__gt=last_read,
                ).exclude(user=user).count()
            else:
                count = Message.objects.filter(
                    channel='support',
                    is_staff_response=True,
                    customer=user,
                    created_at__gt=last_read,
                ).count()
            return {'chat_unread_count': count}
    except Exception:
        pass
    return {'chat_unread_count': 0}
