from django.urls import path

from . import views

urlpatterns = [
    path('orders', views.orders, name='etsy_orders'),
    path('refresh', views.refresh, name='etsy_refresh_auth_token'),
    # path('oauth', views.oauth, name='etsy_oauth'),
    path('', views.index, name='etsy_index'),
]
