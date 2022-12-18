from django.contrib import admin

from .models import Address, Order, OrderItem


class AddressAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "street", "house_number", "zip_code")


class OrderAdmin(admin.ModelAdmin):
    list_display = ("marketplace_order_number", "order_date")


class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order_date",
        "order_number",
        "fulfillment_status",
        "expected_delivery_date",
    )

    @admin.display()
    def order_number(self, obj):
        return obj.order.marketplace_order_number

    @admin.display(ordering="order__order_date")
    def order_date(self, obj):
        return obj.order.order_date


admin.site.register(Address, AddressAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
