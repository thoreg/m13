from django.urls import path

from . import views

urlpatterns = [
    path("authcode-xxx-2013-rand0m", views.authcode, name="tiktok_authcode"),
    path("", views.index, name="tiktok_index"),
]
