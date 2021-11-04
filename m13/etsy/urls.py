from django.urls import path

from . import views

urlpatterns = [
    path('csv', views.orderitems_csv, name='etsy_orderitems_csv'),
    path('orders', views.orders, name='etsy_orders'),
    path('oauth', views.oauth, name='etsy_oauth'),
    path('', views.index, name='etsy_index'),
]
