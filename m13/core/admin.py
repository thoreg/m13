from django.contrib import admin

from .models import Article, Product


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'sku', 'product_ean')

    @admin.display()
    def product_name(self, obj):
        return obj.product.name

    @admin.display()
    def product_ean(self, obj):
        return obj.product.ean


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'ean')


admin.site.register(Article, ArticleAdmin)
admin.site.register(Product, ProductAdmin)
