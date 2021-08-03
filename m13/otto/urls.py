from django.urls import path

from . import views

urlpatterns = [
    path('csv/', views.orderitems_csv, name='orderitems_csv'),
    path('', views.index, name='index'),
]