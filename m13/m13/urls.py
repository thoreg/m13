"""m13 URL Configuration"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from otto.viewsets import OrderItemViewSet as OttoOrderItemsViewSet

router = routers.DefaultRouter()
router.register(r'otto/orderitems', OttoOrderItemsViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('addi/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('otto/', include('otto.urls')),
    path('z/', include('zalando.urls')),
    path('etsy/', include('etsy.urls')),
    path('shipping/', include('shipping.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'm13.views.page_not_found_view'
