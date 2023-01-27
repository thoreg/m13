from django.db import models
from django_extensions.db.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    ean = models.CharField(max_length=13, unique=True)
    name = models.CharField(max_length=256)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)


class Article(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    sku = models.CharField(max_length=32, unique=True)

    class Meta:
        ordering = ["sku"]

    def __str__(self):
        # return self.product.name
        return self.sku


class Price(TimeStampedModel):
    """Central point of price control."""

    article = models.CharField(max_length=32, primary_key=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.PROTECT)
    costs_production = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    vk_zalando = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    vk_otto = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    z_shipping_costs = models.DecimalField(
        default=3.55, max_digits=5, decimal_places=2, null=True, blank=True
    )
    z_return_costs = models.DecimalField(
        default=3.55, max_digits=5, decimal_places=2, null=True, blank=True
    )
    o_shipping_costs = models.DecimalField(
        default=3.55, max_digits=5, decimal_places=2, null=True, blank=True
    )
    o_return_costs = models.DecimalField(
        default=3.55, max_digits=5, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return f"{self.category} : {self.article}"
