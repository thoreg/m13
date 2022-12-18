from django.urls import path

from . import views

urlpatterns = [
    path("csv", views.orderitems_csv, name="etsy_orderitems_csv"),
    path("orders", views.orders, name="etsy_orders"),
    path("oauth", views.oauth, name="etsy_oauth"),
    path("shipments", views.shipments, name="etsy_shipments"),
    path("stats/orderitems", views.stats_orderitems, name="etsy_stats_orderitems"),
    path(
        "upload-tracking-codes/success",
        views.upload_tracking_codes_success,
        name="etsy_upload_tracking_codes_success",
    ),
    path("", views.index, name="etsy_index"),
]
