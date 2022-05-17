from django.contrib import admin

from .models import PriceTool, TransactionFileUpload


class PriceToolAdmin(admin.ModelAdmin):
    list_display = ('z_factor', 'active')


class TransactionFileUploadAdmin(admin.ModelAdmin):
    list_display = (
        'file_name',
        'status_code_upload',
        'status_code_processing',
    )
    readonly_fields = (
        'file_name',
        'original_csv',
        'status_code_upload',
        'status_code_processing',
    )


admin.site.register(PriceTool, PriceToolAdmin)
admin.site.register(TransactionFileUpload, TransactionFileUploadAdmin)
