from django.contrib import admin

from .models import PriceTool


class PriceToolAdmin(admin.ModelAdmin):
    list_display = ('z_factor', 'active')


admin.site.register(PriceTool, PriceToolAdmin)
