from django.contrib import admin

from .models import FeedUpload, Order, OrderLine


@admin.register(FeedUpload)
class FeedUploadAdmin(admin.ModelAdmin):
    list_display = ("created", "feed_type", "status_code", "number_of_items")
    ordering = ("-created",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "booking_id",
        "marketplace_name",
        "marketplace_order_id_1",
        "status",
        "order_date",
        "created",
    )
    list_filter = ("status", "marketplace_name")
    search_fields = ("marketplace_order_id_1", "marketplace_order_id_2", "booking_id")
    ordering = ("-order_date",)


@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = ("line_id", "order", "marketplace_sku", "article_number", "status", "price")
    list_filter = ("status",)
    search_fields = ("marketplace_sku", "article_number", "line_id")
