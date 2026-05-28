from django.db import models
from django_extensions.db.models import TimeStampedModel


class FeedUpload(TimeStampedModel):
    """Track irisOne QuickConnect feed uploads."""

    class FeedType(models.TextChoices):
        FULL = "full", "Full"
        DELTA = "delta", "Delta"
        PRODUCT = "product", "Product"

    feed_type = models.CharField(
        max_length=10, choices=FeedType.choices, default=FeedType.FULL
    )
    status_code = models.PositiveSmallIntegerField()
    number_of_items = models.PositiveIntegerField()
    path_to_csv = models.CharField(max_length=256)


class Order(TimeStampedModel):
    """Order imported from irisOne API."""

    booking_id = models.IntegerField(unique=True)
    order_id = models.IntegerField()
    marketplace_name = models.CharField(max_length=64)
    marketplace_detail = models.CharField(max_length=64, blank=True, default="")
    marketplace_order_id_1 = models.CharField(max_length=128)
    marketplace_order_id_2 = models.CharField(max_length=128, blank=True, default="")
    order_date = models.DateTimeField()
    currency = models.CharField(max_length=8, default="EUR")
    buyer_country = models.CharField(max_length=2, blank=True, default="")

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        OPENED = "opened", "Opened"
        FULFILLED = "fulfilled", "Fulfilled"
        CANCELLED = "cancelled", "Cancelled"

    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    exported = models.BooleanField(default=False)
    origin_labels = models.CharField(max_length=16, blank=True, default="")
    origin_documents = models.CharField(max_length=16, blank=True, default="")
    origin_invoices = models.CharField(max_length=16, blank=True, default="")

    def __str__(self):
        return f"Order({self.booking_id}, {self.marketplace_name}, {self.status})"


class OrderLine(TimeStampedModel):
    """A line item within an irisOne order."""

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="lines")
    line_id = models.IntegerField(unique=True)
    item_id = models.IntegerField()
    line_identifier = models.CharField(max_length=64, blank=True, default="")
    marketplace_sku = models.CharField(max_length=128, blank=True, default="")
    article_number = models.CharField(max_length=64, blank=True, default="")
    price = models.CharField(max_length=16)
    price_net = models.CharField(max_length=16, blank=True, default="")
    vat = models.CharField(max_length=8, blank=True, default="")

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        OPENED = "opened", "Opened"
        FULFILLED = "fulfilled", "Fulfilled"
        CANCELLED = "cancelled", "Cancelled"
        RETURNED = "returned", "Returned"

    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )

    def __str__(self):
        return f"OrderLine({self.line_id}, {self.marketplace_sku}, {self.status})"
