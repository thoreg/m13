from django.contrib import admin

from .models import Address, AuthGrant, AuthToken, Order


class AddressAdmin(admin.ModelAdmin):
    list_display = ("buyer_email", "formatted_address")
    ordering = ("-created",)


class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("created", "token")
    ordering = ("-created",)


class AuthGrantAdmin(admin.ModelAdmin):
    list_display = ("created", "state")
    ordering = ("-created",)


class OrderAdmin(admin.ModelAdmin):
    list_display = ("created", "status")
    ordering = ("-created",)


admin.site.register(Address, AddressAdmin)
admin.site.register(AuthToken, AuthTokenAdmin)
admin.site.register(AuthGrant, AuthGrantAdmin)
admin.site.register(Order, OrderAdmin)
