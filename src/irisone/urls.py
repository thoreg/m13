from django.urls import path

from . import views

urlpatterns = [
    path("feed/", views.feed, name="irisone_feed"),
    path("orders/csv/", views.orders_csv, name="irisone_orders_csv"),
    path("", views.index, name="irisone_index"),
]
