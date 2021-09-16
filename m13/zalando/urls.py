from django.urls import path

from . import views

urlpatterns = [
    path('oea/', views.oea_webhook, name='zalando_oea_webhook'),
    path('', views.index, name='zalando_index')
]
