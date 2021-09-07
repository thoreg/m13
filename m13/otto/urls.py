from django.urls import path

from . import views

urlpatterns = [
    path('csv/', views.orderitems_csv, name='otto_orderitems_csv'),
    path('import-orders/', views.import_orders, name='otto_import_orders'),
    path('upload-tracking-codes/success',
         views.upload_tracking_codes_success,
         name='otto_upload_tracking_codes_success'),
    path('upload-tracking-codes/',
         views.upload_tracking_codes,
         name='otto_upload_tracking_codes'),
    path('stats', views.stats, name='otto_stats'),
    path('', views.index, name='otto_index'),
]
