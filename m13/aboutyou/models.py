from django.db import models
from django_extensions.db.models import TimeStampedModel


class BatchRequest(TimeStampedModel):
    """Track batch requests (e.g. stock updates)."""

    id = models.CharField(primary_key=True)
    started = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, null=True)
    completed = models.DateTimeField(null=True)


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
    marketplace_order_id = models.CharField(max_length=64, unique=True)
    order_date = models.DateTimeField()

    invoice_address = models.ForeignKey(
        Address, related_name="invoice_address_set", null=True, on_delete=models.PROTECT
    )
    delivery_address = models.ForeignKey(
        Address, related_name="delivery_address_set", on_delete=models.PROTECT
    )

    class Status(models.TextChoices):
        OPEN = "open"
        SHIPPED = "shipped"
        CANCELED = "cancelled"
        RETURNED = "returned"
        MIXED = "mixed"

    status = models.CharField(
        max_length=11,
        choices=Status.choices,
        default=Status.OPEN,
    )


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    fulfillment_status = models.CharField(max_length=32)

    price_in_cent = models.PositiveIntegerField()

    position_item_id = models.CharField(max_length=36)
    sku = models.CharField(max_length=36)
    vat_rate = models.PositiveSmallIntegerField()

    # returned_date = models.DateTimeField(null=True, blank=True)
    # sent_date = models.DateTimeField(null=True, blank=True)

    # carrier = models.CharField(max_length=32, null=True, blank=True)
    # carrier_service_code = models.CharField(max_length=128, null=True, blank=True)
    # tracking_number = models.CharField(max_length=128, null=True, blank=True)

    def __repr__(self) -> str:
        return (
            f"({self.order}:{self.order.order_date}) sku: {self.sku} "
            f"price: {self.price_in_cent} "
            f"fulfillment_status: {self.fulfillment_status}"
        )


class Shipment(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    carrier = models.CharField(max_length=128)
    tracking_info = models.CharField(max_length=256)
    response_status_code = models.PositiveSmallIntegerField()
    response = models.JSONField()


class Product(TimeStampedModel):
    """Extra product model for AY which has special product tile for its own."""

    sku = models.CharField(max_length=32)
    product_title = models.CharField(max_length=128)
