from django.urls import path

from . import views

urlpatterns = [
    path('csv/<str:date>/', views.orderitems_csv, name='zalando_orderitems_csv'),
    path('price-feed/', views.price_feed, name='zalando_price_feed'),
    path('oea/', views.oea_webhook, name='zalando_oea_webhook'),
    path('', views.index, name='zalando_index')
]
