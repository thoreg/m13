from django.contrib import admin

from .models import Order, OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'marketplace_order_id',
        'internal_status',
        'created'
    )


class OrderItemAdmin(admin.ModelAdmin):
    def get_marketplace_order_id(self, obj):
        return obj.order.marketplace_order_id

    list_display = (
        'get_marketplace_order_id',
        'billing_text',
        'sku',
        'item_price',
        'created'
    )


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
