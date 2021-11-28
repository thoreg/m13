from django.urls import path

from . import views

urlpatterns = [
    path('success',
         views.upload_shipping_infos_success,
         name='upload_shipping_infos_success'),
    path('', views.index, name='shipping_index'),
]
