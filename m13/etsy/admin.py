from django.contrib import admin

from .models import Address, AuthGrant, AuthToken


class AddressAdmin(admin.ModelAdmin):
    list_display = ("buyer_email", "formatted_address")
    ordering = ("-created",)


class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("created", "token")
    ordering = ("-created",)


class AuthGrantAdmin(admin.ModelAdmin):
    list_display = ("created", "state")
    ordering = ("-created",)


admin.site.register(Address, AddressAdmin)
admin.site.register(AuthToken, AuthTokenAdmin)
admin.site.register(AuthGrant, AuthGrantAdmin)
