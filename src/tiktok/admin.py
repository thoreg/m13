from django.contrib import admin

from .models import Address, AuthToken, Order, OrderItem, Product, Shipment


class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("created", "refresh_token", "token")
    ordering = ("-created",)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("seller_sku", "title", "tiktok_product_id")
    ordering = ("-created",)


class OrderAdmin(admin.ModelAdmin):
    list_display = ("tiktok_order_id", "status")
    ordering = ("-created",)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order__tiktok_order_id",
        "sku",
        "status",
        "tiktok_sku_id",
        "package_id",
        "tiktok_orderitem_id",
    )
    ordering = ("-created",)


class AddressAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "full_address")
    ordering = ("-created",)


class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        "package_id",
        "tracking_number",
        "response_status_code",
    )
    ordering = ("-created",)


admin.site.register(AuthToken, AuthTokenAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Shipment, ShipmentAdmin)
