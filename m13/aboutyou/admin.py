from django.contrib import admin
from django.contrib.admin.options import StackedInline

from .models import Address, BatchRequestTrackingInfo, Order, OrderItem, Product


@admin.register(BatchRequestTrackingInfo)
class BatchRequestTrackingInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "started", "status", "started")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "product_title")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "street", "zip_code")

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return [f.name for f in self.model._meta.fields]
        return ()  # New object, no readonly fields


class OrderItemInline(StackedInline):
    can_delete = False
    extra = 0
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemInline,)
    list_display = ("marketplace_order_id", "order_date")

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return [f.name for f in self.model._meta.fields]
        return ()  # New object, no readonly fields


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "position_item_id",
        "order_id",
        "order_date",
    )
    search_fields = [
        "sku",
        "position_item_id",
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
