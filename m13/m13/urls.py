"""m13 URL Configuration"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from core import views as core_views
from core.viewsets import (
    SalesStatsTop13ReturnViewSet,
    SalesStatsTop13ViewSet,
    SalesVolumeZalandoViewSet,
)
from otto.viewsets import OrderItemViewSet as OttoOrderItemsViewSet
from zalando import viewsets as zalando_viewsets

from .views import index, jobs

router = routers.DefaultRouter()
router.register(r"otto/orderitems", OttoOrderItemsViewSet)
router.register(
    r"zalando/raw-daily-shipement-reports", zalando_viewsets.RawDailyShipmentReportList
)
router.register(r"sales-stats/top13/sales", SalesStatsTop13ViewSet)
router.register(r"sales-stats/top13/return", SalesStatsTop13ReturnViewSet)
router.register(r"sales-stats/z/sales-volume", SalesVolumeZalandoViewSet)

urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/v2/core/return-shipments-stats/", core_views.api_return_shipments_stats),
    path("api/", include(router.urls)),
    path("addi/", include("massadmin.urls")),
    path("addi/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("galaxus/", include("galaxus.urls")),
    path("galeria/", include("galeria.urls")),
    path("otto/", include("otto.urls")),
    path("z/", include("zalando.urls")),
    path("etsy/", include("etsy.urls")),
    path("shipping/", include("shipping.urls")),
    path("tiktok/", include("tiktok.urls")),
    path("core/return-shipments-stats", core_views.return_shipments_stats),
    path("jobs/", jobs),
    path("", index),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = "m13.views.page_not_found_view"
