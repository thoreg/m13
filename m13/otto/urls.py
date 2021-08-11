from django.urls import path

from . import views

urlpatterns = [
    path('csv/', views.orderitems_csv, name='otto_orderitems_csv'),
    path('import-orders/', views.import_orders, name='otto_import_orders'),
    path('upload-tracking-codes/', views.upload_tracking_codes, name='otto_upload_tracking_codes'),
    path('', views.index, name='index'),
]