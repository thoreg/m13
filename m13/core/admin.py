from django.contrib import admin

from .models import Category, Job, MarketplaceConfig, Price, Product


class MarketplaceConfigAdmin(admin.ModelAdmin):
    """Admin interface for configuration of a marketplace and its costs."""

    list_display = (
        "name",
        "shipping_costs",
        "return_costs",
        "active",
        "created",
        "modified",
    )

    def get_readonly_fields(self, _request, obj=None):
        """Make entry read only once it has been created."""
        if obj:
            return [
                "name",
                "shipping_costs",
                "return_costs",
                "active",
                "created",
                "modified",
            ]
        else:
            return []

    def has_delete_permission(self, _request, _obj=None):
        """Deletion of a marketplace is not allowed - there might be related values."""
        return False


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "ean")

    @admin.display()
    def category(self, obj):
        return obj.category.name


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


class JobAdmin(admin.ModelAdmin):
    list_display = (
        "cmd",
        "successful",
        "runtime",
        "start",
        "end",
    )

    @admin.display()
    def runtime(self, obj):
        runtime = 0
        if obj.end:
            runtime = obj.end - obj.start
        return runtime


class PriceAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "category",
        "vk_zalando",
        "vk_otto",
    )

    search_fields = [
        "sku",
    ]

    @admin.display()
    def category(self, obj):
        return obj.category.name


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(MarketplaceConfig, MarketplaceConfigAdmin)
admin.site.register(Job, JobAdmin)
