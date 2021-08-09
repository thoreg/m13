from django.urls import path

from . import views

urlpatterns = [
    path('csv/', views.orderitems_csv, name='otto_orderitems_csv'),
    path('import-orders/', views.import_orders, name='otto_import_orders'),
    path('', views.index, name='index'),
]