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
