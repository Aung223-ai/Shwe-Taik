from django.urls import path
from .views import *

urlpatterns = [
    path('', cats, name='all-cats'),
    path('reorder/', cats_reorder, name='cats-reorder'),
    path('create/', cat_create, name='cat-create'),
    path('edit/', cat_edit_list, name='cat-edit-list'),
    path('<int:cat_id>/edit/', cat_edit, name='cat-edit'),
    path('<int:cat_id>/products/', cat_products, name='cat-products'),
    path('subs/', subs, name='all-sub-cats'),
    path('subs/<int:sub_id>/', sub_detail, name='sub-detail'),
    path('subs/<int:sub_id>/favorite/', toggle_favorite, name='toggle-favorite'),
    path('subs/<int:sub_id>/favorite-guest/', toggle_favorite_guest, name='toggle-favorite-guest'),
    path('favorites/', favorites, name='favorites'),
    path('favorites/reorder/', favorites_reorder, name='favorites-reorder'),
    path('subs/edit/', sub_edit_list, name='sub-edit-list'),
    path('subs/<int:sub_id>/edit/', sub_edit, name='sub-edit'),
    path('subs/<int:sub_id>/add-to-cart/', add_to_cart, name='add-to-cart'),
    path('subs/<int:sub_id>/add-to-cart-guest/', add_to_cart_guest, name='add-to-cart-guest'),
    path('subs/<int:sub_id>/buy-now/', buy_now, name='buy-now'),
    path('subs/<int:sub_id>/buy-now-guest/', buy_now_guest, name='buy-now-guest'),
    path('cart/', cart_view, name='cart'),
    path('cart/<int:item_id>/<str:action>/', update_cart, name='update-cart'),
    path('orders/<int:order_id>/<str:status>/', order_update_status, name='order-update-status'),
    path('subs/create/', create, name='sub-create'),
]
