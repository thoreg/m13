from django.urls import path

from . import views

urlpatterns = [
    path("price-feed/", views.price_feed, name="galeria_price_feed"),
    path("", views.index, name="galeria_index"),
]
