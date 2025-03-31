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


class Address(TimeStampedModel):
    city = models.CharField(max_length=32)
    country_code = models.CharField(max_length=32)
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(max_length=64)
    full_address = models.CharField(max_length=128)
    last_name = models.CharField(max_length=64)
    street = models.CharField(max_length=128)
    zip_code = models.CharField(max_length=32)


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        """Specific order status."""

        UNPAID = "UNPAID"
        # The order has been placed, but payment has not been completed.
        ON_HOLD = "ON_HOLD"
        # The order has been accepted and is awaiting fulfillment.
        # The buyer may still cancel without the seller’s approval.
        # If order_type=PRE_ORDER, the product is still awaiting release
        # so payment will only be authorized 1 day before the release,
        # but the seller should start preparing for the release.
        # (Applicable only for the US and UK market).
        AWAITING_SHIPMENT = "AWAITING_SHIPMENT"
        # The order is ready to be shipped, but no items have been shipped yet.
        PARTIALLY_SHIPPING = "PARTIALLY_SHIPPING"
        # Some items in the order have been shipped, but not all.
        AWAITING_COLLECTION = "AWAITING_COLLECTION"
        # Shipping has been arranged, but the package is waiting to be collected by the carrier.
        IN_TRANSIT = "IN_TRANSIT"
        # The package has been collected by the carrier and delivery is in progress.
        DELIVERED = "DELIVERED"
        # The package has been delivered to the buyer.
        COMPLETED = "COMPLETED"
        # The order has been completed, and no further returns or refunds are allowed.
        CANCELLED = "CANCELLED"
        # The order has been cancelled.

    status = models.CharField(
        max_length=24,
        choices=Status,
        null=True,
    )

    buyer_email = models.EmailField()
    tiktok_order_id = models.CharField(max_length=24)
    create_time = models.DateTimeField()
    rts_sla_time = models.DateTimeField()
    # The latest shipping time specified by the platform. Unix timestamp.

    delivery_address = models.ForeignKey(
        Address, related_name="delivery_address_set", on_delete=models.PROTECT
    )
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2)


class OrderItem(TimeStampedModel):
    class Status(models.TextChoices):
        """Specific orderitem status."""

        UNPAID = "UNPAID"
        ON_HOLD = "ON_HOLD"
        AWAITING_SHIPMENT = "AWAITING_SHIPMENT"
        PARTIALLY_SHIPPING = "PARTIALLY_SHIPPING"
        AWAITING_COLLECTION = "AWAITING_COLLECTION"
        IN_TRANSIT = "IN_TRANSIT"
        DELIVERED = "DELIVERED"
        COMPLETED = "COMPLETED"
        CANCELLED = "CANCELLED"

    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    tiktok_orderitem_id = models.CharField(max_length=24)
    tiktok_sku_id = models.CharField(max_length=24)
    tiktok_product_name = models.CharField(max_length=128)
    package_id = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    sku = models.CharField(max_length=24)
    status = models.CharField(
        max_length=24,
        choices=Status,
        null=True,
    )


class Shipment(TimeStampedModel):
    """Shipment model to hold shipment information."""

    tracking_number = models.CharField(max_length=128)
    package_id = models.CharField(max_length=128)
    response_status_code = models.IntegerField(null=True)
    response = models.TextField(null=True)
