from django.contrib import admin

from .models import Address, BatchRequestTrackingInfo, Order, OrderItem, Product


class BatchRequestTrackingInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "started", "tracking_info")


class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "product_title")


class AddressAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "street", "zip_code")

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return [f.name for f in self.model._meta.fields]
        return ()  # New object, no readonly fields


class OrderAdmin(admin.ModelAdmin):
    list_display = ("marketplace_order_id", "order_date")

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return [f.name for f in self.model._meta.fields]
        return ()  # New object, no readonly fields


class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "order_id",
        "order_date",
    )
    search_fields = [
        "sku",
    ]

    @admin.display()
    def order_id(self, obj):
        return obj.order.marketplace_order_id

    @admin.display(ordering="order__order_date")
    def order_date(self, obj):
        return obj.order.order_date

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return [f.name for f in self.model._meta.fields]
        return ()  # New object, no readonly fields


admin.site.register(Address, AddressAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(BatchRequestTrackingInfo, BatchRequestTrackingInfoAdmin)
