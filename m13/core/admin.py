from django.contrib import admin

from .models import Article, Category, Product


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'sku', 'product_ean')

    @admin.display()
    def product_name(self, obj):
        return obj.product.name

    @admin.display()
    def product_ean(self, obj):
        return obj.product.ean

    @admin.display()
    def category(self, obj):
        if obj.product.category:
            return obj.product.category.name


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'ean')

    @admin.display()
    def category(self, obj):
        return obj.category.name


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


admin.site.register(Article, ArticleAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
