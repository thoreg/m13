from django.contrib import admin
from massadmin.massadmin import MassEditMixin

from .models import Category, Error, Job, MarketplaceConfig, Price, Product


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


class PriceAdmin(MassEditMixin, admin.ModelAdmin):
    list_display = (
        "sku",
        "category",
        "vk_zalando",
        "pimped_zalando",
        "vk_otto",
    )
    massadmin_exclude = [
        "sku",
    ]

    search_fields = [
        "sku",
    ]

    @admin.display()
    def category(self, obj):
        return obj.category.name

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.order_by("name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ErrorAdmin(admin.ModelAdmin):
    list_display = ("created", "msg", "comment", "cleared")
    ordering = ("-created",)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(MarketplaceConfig, MarketplaceConfigAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Error, ErrorAdmin)
