from django.contrib import admin

from .models import Order, OrderItem


class OrderItemAdmin(admin.ModelAdmin):
    def get_marketplace_order_id(self, obj):
        return obj.order.marketplace_order_id

    list_display = (
        "get_marketplace_order_id",
        "sku",
        "price",
        "created",
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ("marketplace_order_id", "internal_status", "created")


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
