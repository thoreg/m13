from django.urls import path

from . import views

urlpatterns = [
    path("csv/", views.orderitems_csv, name="ay_orderitems_csv"),
    path("import-orders/", views.import_orders, name="ay_import_orders"),
    path(
        "upload-tracking-codes/success",
        views.upload_tracking_codes_success,
        name="ay_upload_tracking_codes_success",
    ),
    path(
        "upload-tracking-codes/",
        views.upload_tracking_codes,
        name="ay_upload_tracking_codes",
    ),
    path("", views.index, name="ay_index"),
]
