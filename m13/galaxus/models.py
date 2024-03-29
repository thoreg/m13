from django.db import models
from django_extensions.db.models import TimeStampedModel


class Address(TimeStampedModel):
    """Customer address in Galaxus"""

    city = models.CharField(max_length=128)
    country_code = models.CharField(max_length=32)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    title = models.CharField(max_length=32, null=True, blank=True)
    zip_code = models.CharField(max_length=32)


class Order(TimeStampedModel):
    marketplace_order_id = models.CharField(max_length=64)
    marketplace_order_number = models.CharField(max_length=32)
    order_date = models.DateTimeField()
    invoice_address = models.ForeignKey(
        Address, related_name="invoice_address_set", null=True, on_delete=models.PROTECT
    )
    delivery_address = models.ForeignKey(
        Address, related_name="delivery_address_set", on_delete=models.PROTECT
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

    delivery_fee = models.JSONField()
    mail = models.EmailField()


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    expected_delivery_date = models.DateTimeField()
    fulfillment_status = models.CharField(max_length=32)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()

    position_item_id = models.CharField(max_length=36)
    ean = models.CharField(max_length=16)
    product_title = models.CharField(max_length=256)
    sku = models.CharField(max_length=36)

    returned_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)

    carrier = models.CharField(max_length=32, null=True, blank=True)
    carrier_service_code = models.CharField(max_length=128, null=True, blank=True)
    tracking_number = models.CharField(max_length=128, null=True, blank=True)


class Shipment(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    carrier = models.CharField(max_length=128)
    tracking_info = models.CharField(max_length=256)
    response_status_code = models.PositiveSmallIntegerField()
    response = models.JSONField()
