"""m13 URL Configuration"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from otto.viewsets import OrderItemViewSet as OttoOrderItemsViewSet
from zalando import views as zalando_views
from zalando import viewsets as zalando_viewsets

from .views import index

router = routers.DefaultRouter()
router.register(r'otto/orderitems', OttoOrderItemsViewSet)
router.register(r'zalando/raw-daily-shipement-reports', zalando_viewsets.RawDailyShipmentReportList)

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('api/zalando/finance/products/<str:pk>/', zalando_viewsets.ZProductDetail.as_view()),
    path('api/zalando/finance/products/', zalando_viewsets.ZProductList.as_view()),
    path('api/v1/zalando/finance/products/', zalando_views.product_stats_v1),
    path('api/zalando/finance/article-stats/', zalando_views.article_stats),
    path('api/', include(router.urls)),
    path('addi/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('mirapodo/', include('mirapodo.urls')),
    path('otto/', include('otto.urls')),
    path('z/', include('zalando.urls')),
    path('etsy/', include('etsy.urls')),
    path('shipping/', include('shipping.urls')),
    path('', index)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'm13.views.page_not_found_view'
