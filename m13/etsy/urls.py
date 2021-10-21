from django.urls import path

from . import views

urlpatterns = [
    path('oauth', views.index, name='etsy_oauth'),
    path('', views.index, name='etsy_index'),
]
