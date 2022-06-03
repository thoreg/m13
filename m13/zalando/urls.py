from django.urls import path

from . import views

urlpatterns = [
    path('csv/<str:day>/', views.orderitems_csv, name='zalando_orderitems_csv'),
    path('price-feed/', views.price_feed, name='zalando_price_feed'),
    path('oea/', views.oea_webhook, name='zalando_oea_webhook'),
    path('stats/orderitems', views.stats_orderitems, name='zalando_stats_orderitems'),
    path('finance/upload', views.upload_files, name='zalando_finance_upload_files'),
    path('finance/calculator', views.calculator, name='zalando_finance_calculator'),
    path('', views.index, name='zalando_index')
]
