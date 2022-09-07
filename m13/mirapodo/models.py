from django.db import models
from django.db.models.aggregates import Count
from django_extensions.db.models import TimeStampedModel


class Address(TimeStampedModel):
    """We get from otto only shipping and billing addresses.

    No customer id - no email
    """
    addition = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=128)
    country_code = models.CharField(max_length=32)
    first_name = models.CharField(max_length=128)
    house_number = models.CharField(max_length=16)
    last_name = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    title = models.CharField(max_length=32, null=True, blank=True)
    zip_code = models.CharField(max_length=32)


class Order(TimeStampedModel):
    marketplace_order_id = models.CharField(max_length=64)
    order_date = models.DateTimeField()

    invoice_address = models.ForeignKey(
        Address,
        related_name="invoice_address_set",
        null=True,
        on_delete=models.PROTECT
    )
    delivery_address = models.ForeignKey(
        Address,
        related_name="delivery_address_set",
        on_delete=models.PROTECT
    )

    class Status(models.TextChoices):
        IMPORTED = "IMPORTED", "Imported"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        SHIPPED = "SHIPPED", "Shipped"
        FINISHED = "FINISHED", "Finished"
        CANCELED = "CANCELED", "Canceled"

    internal_status = models.CharField(
        max_length=11,
        choices=Status.choices,
        default=Status.IMPORTED,
    )

    delivery_fee = models.CharField(max_length=32)


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)

    billing_text = models.CharField(max_length=32)
    channel_id = models.CharField(max_length=2)
    channeld_sku = models.CharField(max_length=32)
    date_created = models.DateTimeField()
    ean = models.CharField(max_length=13)
    item_price = models.DecimalField(max_digits=5, decimal_places=2)
    quantity = models.PositiveIntegerField()
    sku = models.CharField(max_length=16)
    position_item_id = models.CharField(max_length=16)
    transfer_price = models.DecimalField(max_digits=5, decimal_places=2)
