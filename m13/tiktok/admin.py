from django.contrib import admin

from .models import AuthToken, Product


class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("created", "refresh_token", "token")
    ordering = ("-created",)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("seller_sku", "title", "tiktok_product_id")
    ordering = ("-created",)


admin.site.register(AuthToken, AuthTokenAdmin)
admin.site.register(Product, ProductAdmin)
