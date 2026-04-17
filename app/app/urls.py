from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static 
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('reorder/', views.home_reorder, name='home-reorder'),
    path('edit/', views.home_edit_view, name='home-edit'),
    path('edit/section/<int:section_id>/delete/', views.home_section_delete, name='home-section-delete'),
    path('landing/', views.landing_view, name='landing'),
    path('landing/edit/', views.landing_edit_view, name='landing-edit'),
    path('shop/', include('category.urls')),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile-edit'),
    path('message-center/', views.message_center_view, name='message-center'),
    path('messages/', views.messages_view, name='messages'),
    path('logout/', views.logout_view, name='logout'),
]

if settings.DEBUG:
    print("DEBUG is True, adding MEDIA patterns")
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
