from django.urls import path

from . import views

urlpatterns = [
    path("csv/", views.orderitems_csv, name="galaxus_orderitems_csv"),
    path("import-orders/", views.import_orders, name="galaxus_import_orders"),
    path("", views.index, name="galaxus_index"),
]
