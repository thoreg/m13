from django.contrib import admin

from .models import Address, AuthGrant, AuthToken, Order, OrderItem


class AddressAdmin(admin.ModelAdmin):
    list_display = ("buyer_email", "formatted_address")
    ordering = ("-created",)


class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("created", "token")
    ordering = ("-created",)


class AuthGrantAdmin(admin.ModelAdmin):
    list_display = ("created", "state")
    ordering = ("-created",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ("created", "status", "marketplace_order_id")
    ordering = ("-created",)


admin.site.register(Address, AddressAdmin)
admin.site.register(AuthToken, AuthTokenAdmin)
admin.site.register(AuthGrant, AuthGrantAdmin)
admin.site.register(Order, OrderAdmin)
