from decimal import Decimal

from django.db import models
from django_extensions.db.models import TimeStampedModel

from core.models import Article


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

    orig_created_timestamp = models.DateTimeField(null=True)
    orig_modified_timestamp = models.DateTimeField(null=True)


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


class TransactionFileUpload(TimeStampedModel):
    """Upload of CSV files which contain detailed information about transactions."""
    processed = models.BooleanField(default=False)
    original_csv = models.FileField(upload_to='zalando/finance/')
    file_name = models.CharField(max_length=64, unique=True)

    def __repr__(self):
        return f'ZalandoTransactionFile({self.original_csv})'


class DailyShipmentReport(TimeStampedModel):
    """Relevant data from daily shipment reports from Zalando."""
    article_number = models.CharField(max_length=36)
    cancel = models.BooleanField(default=False)
    channel_order_number = models.CharField(max_length=16)
    order_created = models.DateTimeField()
    price_in_cent = models.PositiveIntegerField()
    return_reason = models.CharField(max_length=256)
    returned = models.BooleanField(default=False)
    shipment = models.BooleanField(default=False)


def _r(value):
    """Return rounded value."""
    return round(value, 2)


class ZCalculator(TimeStampedModel):
    article = models.OneToOneField(
        Article,
        on_delete=models.PROTECT,
        primary_key=True,
    )
    costs_production = models.DecimalField(max_digits=6, decimal_places=2)              # B2
    vk_zalando = models.DecimalField(max_digits=6, decimal_places=2)                    # C2
    shipping_costs = models.DecimalField(default=3.55, max_digits=5, decimal_places=2)  # D2
    return_costs = models.DecimalField(default=3.55, max_digits=5, decimal_places=2)    # E2

    @property
    def eight_percent_provision(self):                                                  # F2
        """8% =SUM(C2/1,08-C2)"""
        return _r(self.vk_zalando / Decimal('1.08') - self.vk_zalando)

    @property
    def nineteen_percent_vat(self):                                                     # G2
        """19% =SUM(C2/1,19-C2)"""
        return _r(self.vk_zalando / Decimal('1.19') - self.vk_zalando)

    @property
    def generic_costs(self):                                                            # H2
        """Generic costs =SUM(C2*1,03-C2)"""
        return _r(self.vk_zalando * Decimal('1.03') - self.vk_zalando)

    @property
    def profit_after_taxes(self):                                                       # I2
        """=SUM(C2-B2-D2+F2+G2+H2)"""
        base = self.vk_zalando - self.costs_production - self.shipping_costs
        return _r(
            base + self.eight_percent_provision + self.nineteen_percent_vat + self.generic_costs)
