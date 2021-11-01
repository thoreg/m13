from django.contrib import admin

from .models import Address, AuthRequest2


class AddressAdmin(admin.ModelAdmin):
    list_display = ('buyer_email', 'formatted_address')
    ordering = ('-created',)


class AuthRequest2Admin(admin.ModelAdmin):
    list_display = ('created', 'state')
    ordering = ('-created',)


admin.site.register(Address, AddressAdmin)
admin.site.register(AuthRequest2, AuthRequest2Admin)
