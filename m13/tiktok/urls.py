from django.urls import path

from . import views

urlpatterns = [
    path("authcode-xxx-2013-rand0m", views.authcode, name="tiktok_authcode"),
    path("csv/", views.orderitems_csv, name="tiktok_orderitems_csv"),
    path("import-orders/", views.import_orders, name="tiktok_import_orders"),
    path(
        "upload-tracking-codes/success",
        views.upload_tracking_codes_success,
        name="tiktok_upload_tracking_codes_success",
    ),
    path(
        "upload-tracking-codes/",
        views.upload_tracking_codes,
        name="tiktok_upload_tracking_codes",
    ),
    path("", views.index, name="tiktok_index"),
]
