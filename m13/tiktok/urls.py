from django.urls import path

from . import views

urlpatterns = [
    path("authcode", views.authcode, name="tiktok_authcode"),
    path("", views.index, name="tiktok_index"),
]
