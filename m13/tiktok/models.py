from django.db import models
from django_extensions.db.models import TimeStampedModel


class AuthToken(TimeStampedModel):
    """Table to hold access and refresh tokens for TikTok."""

    token = models.CharField(max_length=1024)
    refresh_token = models.CharField(max_length=128)


class Product(TimeStampedModel):
    """Mapping for sku <-> product_id"""

    seller_sku = models.CharField(max_length=64, primary_key=True, editable=False)
    tiktok_product_id = models.CharField(max_length=128, editable=False)
    sku_id = models.CharField(max_length=128, editable=False)
    warehouse_id = models.CharField(max_length=128, editable=False)
    status = models.CharField(max_length=32, editable=False)
    title = models.CharField(max_length=256, editable=False)
