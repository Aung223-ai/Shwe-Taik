from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=30, blank=True, default='')
    address = models.TextField(blank=True, default='')
    last_message_read_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='support_threads')
    channel = models.CharField(max_length=20, default='support')
    text = models.TextField()
    is_staff_response = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.created_at:%Y-%m-%d %H:%M}'


class LandingContent(models.Model):
    hero_title = models.CharField(max_length=255, blank=True, default='')
    hero_subtitle = models.CharField(max_length=255, blank=True, default='')
    trust_line = models.CharField(max_length=255, blank=True, default='')
    about_text = models.TextField(blank=True, default='')
    mission_text = models.TextField(blank=True, default='')
    vision_text = models.TextField(blank=True, default='')
    services_text = models.TextField(blank=True, default='')
    projects_1 = models.CharField(max_length=255, blank=True, default='')
    projects_2 = models.CharField(max_length=255, blank=True, default='')
    projects_3 = models.CharField(max_length=255, blank=True, default='')
    activities_1 = models.CharField(max_length=255, blank=True, default='')
    activities_2 = models.CharField(max_length=255, blank=True, default='')
    activities_3 = models.CharField(max_length=255, blank=True, default='')
    testimonial_1 = models.CharField(max_length=255, blank=True, default='')
    testimonial_2 = models.CharField(max_length=255, blank=True, default='')
    testimonial_3 = models.CharField(max_length=255, blank=True, default='')
    partner_1 = models.CharField(max_length=255, blank=True, default='')
    partner_2 = models.CharField(max_length=255, blank=True, default='')
    partner_3 = models.CharField(max_length=255, blank=True, default='')
    partner_4 = models.CharField(max_length=255, blank=True, default='')
    faq1_q = models.CharField(max_length=255, blank=True, default='')
    faq1_a = models.CharField(max_length=255, blank=True, default='')
    faq2_q = models.CharField(max_length=255, blank=True, default='')
    faq2_a = models.CharField(max_length=255, blank=True, default='')
    newsletter_text = models.CharField(max_length=255, blank=True, default='')
    contact_phone = models.CharField(max_length=100, blank=True, default='')
    contact_email = models.CharField(max_length=100, blank=True, default='')
    contact_address = models.CharField(max_length=255, blank=True, default='')
    careers_text = models.CharField(max_length=255, blank=True, default='')
    cta_title = models.CharField(max_length=255, blank=True, default='')
    cta_button_text = models.CharField(max_length=100, blank=True, default='')


class HomeContent(models.Model):
    video_url = models.CharField(max_length=255, blank=True, default='')
    photo_1 = models.CharField(max_length=255, blank=True, default='')
    photo_2 = models.CharField(max_length=255, blank=True, default='')
    photo_3 = models.CharField(max_length=255, blank=True, default='')
    best_title = models.CharField(max_length=255, blank=True, default='')
    recommend_title = models.CharField(max_length=255, blank=True, default='')
    hero_photo_1 = models.ImageField(upload_to='home/', blank=True, null=True)
    hero_photo_2 = models.ImageField(upload_to='home/', blank=True, null=True)
    hero_photo_3 = models.ImageField(upload_to='home/', blank=True, null=True)


class HomeMedia(models.Model):
    MEDIA_TYPES = (
        ('video', 'Video'),
        ('photo', 'Photo'),
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='home/')
    created_at = models.DateTimeField(auto_now_add=True)


class HomeSection(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, default='')
    product = models.ForeignKey('category.SubCategory', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
