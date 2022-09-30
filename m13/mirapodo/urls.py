from django.urls import path

from . import views

urlpatterns = [
    path('csv/', views.orderitems_csv, name='mirapodo_orderitems_csv'),
    path('import-orders/', views.import_orders, name='mirapodo_import_orders'),
    path('', views.index, name='mirapodo_index'),
]
