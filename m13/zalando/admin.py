from django.contrib import admin

from .models import DailyShipmentReport, PriceTool, TransactionFileUpload


class PriceToolAdmin(admin.ModelAdmin):
    list_display = ('z_factor', 'active')


class TransactionFileUploadAdmin(admin.ModelAdmin):
    list_display = (
        'file_name',
        'processed'
    )
    readonly_fields = (
        'file_name',
        'original_csv',
        'processed'
    )


class DailyShipmentReportAdmin(admin.ModelAdmin):
    list_display = (
        'article_number',
        'order_created',
        'cancel',
        'returned',
        'shipment',
    )
    readonly_fields = (
        'article_number',
        'cancel',
        'channel_order_number',
        'order_created',
        'price_in_cent',
        'return_reason',
        'returned',
        'shipment',
    )


admin.site.register(DailyShipmentReport, DailyShipmentReportAdmin)
admin.site.register(PriceTool, PriceToolAdmin)
admin.site.register(TransactionFileUpload, TransactionFileUploadAdmin)
