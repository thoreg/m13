from django.contrib import admin

from .models import (
    RawDailyShipmentReport,
    PriceTool,
    TransactionFileUpload,
    ZCost,
    ZProduct,
)


class PriceToolAdmin(admin.ModelAdmin):
    list_display = ("z_factor", "active")


class TransactionFileUploadAdmin(admin.ModelAdmin):
    list_display = ("file_name", "processed")
    readonly_fields = ("file_name", "original_csv", "processed")


class RawDailyShipmentReportAdmin(admin.ModelAdmin):
    list_display = (
        "article_number",
        "order_created",
        "order_event_time",
        "cancel",
        "returned",
        "shipment",
    )
    readonly_fields = (
        "article_number",
        "cancel",
        "channel_order_number",
        "order_created",
        "order_event_time",
        "price_in_cent",
        "return_reason",
        "returned",
        "shipment",
    )
    search_fields = [
        "article_number",
    ]


admin.site.register(RawDailyShipmentReport, RawDailyShipmentReportAdmin)
admin.site.register(TransactionFileUpload, TransactionFileUploadAdmin)
