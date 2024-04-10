from django.db import models
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
    email = models.EmailField(null=True, blank=True)


class Order(TimeStampedModel):
    marketplace_order_id = models.CharField(max_length=64)
    marketplace_order_number = models.CharField(max_length=32)
    order_date = models.DateTimeField()
    last_modified_date = models.DateTimeField()

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


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    expected_delivery_date = models.DateTimeField()
    fulfillment_status = models.CharField(max_length=32)

    price_in_cent = models.PositiveIntegerField()
    currency = models.CharField(max_length=8)

    position_item_id = models.CharField(max_length=36)
    article_number = models.CharField(max_length=36)
    ean = models.CharField(max_length=16)
    product_title = models.CharField(max_length=256)
    sku = models.CharField(max_length=36)
    vat_rate = models.PositiveSmallIntegerField()

    returned_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)

    carrier = models.CharField(max_length=32, null=True, blank=True)
    carrier_service_code = models.CharField(max_length=128, null=True, blank=True)
    tracking_number = models.CharField(max_length=128, null=True, blank=True)

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


class StatsOrderItems(models.Model):
    month = models.DateTimeField()
    status = models.CharField(max_length=16)
    count = models.IntegerField()
    revenue = models.FloatField()

    class Meta:
        managed = False
        db_table = "otto_orderitem_stats"


class OrderItemJournal(TimeStampedModel):
    """Entity to keep track of orderitems - used by OCalculator."""

    class OrderItemStatus(models.TextChoices):
        """Otto internal status of OrderItem"""

        ANNOUNCED = "ANNOUNCED"
        PROCESSABLE = "PROCESSABLE"
        SENT = "SENT"
        RETURNED = "RETURNED"
        CANCELLED_BY_PARTNER = "CANCELLED_BY_PARTNER"
        CANCELLED_BY_MARKETPLACE = "CANCELLED_BY_MARKETPLACE"

    sku = models.CharField(max_length=32)
    ean = models.CharField(max_length=16)
    position_item_id = models.CharField(max_length=64)
    order_number = models.CharField(max_length=16)
    fulfillment_status = models.CharField(
        max_length=24,
        choices=OrderItemStatus.choices,
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)
    last_modified = models.DateTimeField()
    """
    # when RETURNED
    'returnedDate': '2024-03-22T08:29:02.118+0000',
    # otherwise
    'sentDate': '2024-03-10T16:27:29.315+0000',
    """

    def __repr__(self) -> str:
        info = [
            f"order_number {self.order_number}",
            f"{self.position_item_id}",
            f"{self.fulfillment_status}",
        ]
        return " : ".join(info)

    @property
    def sent_exist(self) -> bool:
        """Return True if there is more than one journal entry for the orderitem."""
        objects = OrderItemJournal.objects.filter(
            position_item_id=self.position_item_id
        )
        return len(objects) > 1
