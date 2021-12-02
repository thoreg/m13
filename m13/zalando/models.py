from django.db import models
from django_extensions.db.models import TimeStampedModel


class FeedUpload(TimeStampedModel):
    """Track when we did which feed upload."""
    status_code_validation = models.PositiveSmallIntegerField()
    status_code_feed_upload = models.PositiveSmallIntegerField()
    number_of_valid_items = models.PositiveIntegerField()
    path_to_original_csv = models.CharField(max_length=128)
    path_to_pimped_csv = models.CharField(max_length=128)
    z_factor = models.DecimalField(max_digits=3, decimal_places=2)


class PriceTool(TimeStampedModel):
    z_factor = models.DecimalField(max_digits=3, decimal_places=2)
    active = models.BooleanField(default=False)


class OEAWebhookMessage(TimeStampedModel):
    """Order Event API Message."""
    payload = models.JSONField(default=None, null=True)
    processed = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['created']),
        ]


class Address(TimeStampedModel):
    """Address format from Z."""
    line = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=128)
    country_code = models.CharField(max_length=32)
    first_name = models.CharField(max_length=128)
    house_number = models.CharField(max_length=16)
    last_name = models.CharField(max_length=128)
    zip_code = models.CharField(max_length=32)


class Order(TimeStampedModel):
    marketplace_order_id = models.CharField(max_length=64)
    marketplace_order_number = models.CharField(max_length=32)
    order_date = models.DateTimeField()
    last_modified_date = models.DateTimeField()
    store_id = models.CharField(max_length=8)

    delivery_address = models.ForeignKey(
        Address,
        related_name="delivery_address_set",
        null=True,
        on_delete=models.PROTECT
    )

    class Status(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        FULFILLED = "FULFILLED", "Fulfilled"
        ROUTED = "ROUTED", "Routed"
        CANCELLED = "CANCELLED", "Cancelled"
        RETURNED = "RETURNED", "Returned"

    status = models.CharField(
        max_length=11,
        choices=Status.choices,
        default=Status.ASSIGNED,
    )


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    fulfillment_status = models.CharField(max_length=32)

    price_in_cent = models.PositiveIntegerField()
    currency = models.CharField(max_length=8)

    position_item_id = models.CharField(max_length=36)
    article_number = models.CharField(max_length=36)
    ean = models.CharField(max_length=16)

    carrier = models.CharField(max_length=32, null=True, blank=True)
    tracking_number = models.CharField(max_length=128, null=True, blank=True)


class Shipment(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    carrier = models.CharField(max_length=128)
    tracking_info = models.CharField(max_length=256)
    response_status_code = models.PositiveSmallIntegerField()
    response = models.JSONField()


class Product(TimeStampedModel):
    ean = models.CharField(max_length=16, unique=True)
    title = models.CharField(max_length=256)


class StatsOrderItems(models.Model):
    month = models.DateTimeField()
    status = models.CharField(max_length=16)
    count = models.IntegerField()
    revenue = models.FloatField()

    class Meta:
        managed = False
        db_table = 'zalando_orderitem_stats'
