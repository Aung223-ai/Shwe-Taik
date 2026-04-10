from django.contrib import admin
from .models import Profile, Message


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'customer', 'channel', 'is_staff_response', 'created_at')
    list_filter = ('channel', 'is_staff_response',)
    search_fields = ('user__username', 'text')
