from django.contrib import admin

from .models import AuthRequest2


class AuthRequest2Admin(admin.ModelAdmin):
    list_display = ('created', 'state')
    ordering = ('-created',)


admin.site.register(AuthRequest2, AuthRequest2Admin)
