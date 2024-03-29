from decimal import Decimal

from django.db import models
from django_extensions.db.models import TimeStampedModel

from core.models import Category


class FeedUpload(TimeStampedModel):
    """Track when we did which feed upload."""

    status_code_validation = models.PositiveSmallIntegerField()
    status_code_feed_upload = models.PositiveSmallIntegerField()
    number_of_valid_items = models.PositiveIntegerField()
    path_to_original_csv = models.CharField(max_length=128)
    path_to_pimped_csv = models.CharField(max_length=128)
    z_factor = models.DecimalField(max_digits=3, decimal_places=2)
    validation_result = models.TextField()


class PriceTool(TimeStampedModel):
    z_factor = models.DecimalField(max_digits=3, decimal_places=2)
    active = models.BooleanField(default=False)


class OEAWebhookMessage(TimeStampedModel):
    """Order Event API Message."""

    payload = models.JSONField(default=None, null=True)
    processed = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["created"]),
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
        on_delete=models.PROTECT,
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
        db_table = "zalando_orderitem_stats"


class TransactionFileUpload(TimeStampedModel):
    """Upload of CSV files which contain detailed information about transactions."""

    processed = models.BooleanField(default=False)
    original_csv = models.FileField(upload_to="zalando/finance/")
    file_name = models.CharField(max_length=64, unique=True)

    def __repr__(self):
        return f"ZalandoTransactionFile({self.original_csv})"

    class Meta:
        db_table = "zalando_dailyshipmentreport_file_upload"


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


class SalesReportImport(TimeStampedModel):
    """Model to track report imports"""

    name = models.CharField(max_length=256, unique=True)
    """File name of the report"""


class SalesReportExport(TimeStampedModel):
    month = models.PositiveIntegerField()
    """YYYYMM month which this report is about"""
    report = models.JSONField()
    """The complete report as JSON (used for CSV export)"""
    import_reference = models.ForeignKey(SalesReportImport, on_delete=models.PROTECT)
    """Reference to the original import"""


class ZProduct(TimeStampedModel):
    article = models.CharField(max_length=32, primary_key=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.PROTECT)
    costs_production = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )  # B2
    vk_zalando = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )  # C2
    shipping_costs = models.DecimalField(
        default=3.55, max_digits=5, decimal_places=2, null=True, blank=True
    )  # D2
    return_costs = models.DecimalField(
        default=3.55, max_digits=5, decimal_places=2, null=True, blank=True
    )  # E2
    shipped = models.PositiveIntegerField(null=True, blank=True)
    returned = models.PositiveIntegerField(null=True, blank=True)
    canceled = models.PositiveIntegerField(null=True, blank=True)
    pimped = models.BooleanField(default=False)

    @property
    def eight_percent_provision(self):  # F2
        """8% =SUM(C2/1,08-C2)"""
        if self.vk_zalando:
            return _r(self.vk_zalando / Decimal("1.08") - self.vk_zalando)

    @property
    def nineteen_percent_vat(self):  # G2
        """19% =SUM(C2/1,19-C2)"""
        if self.vk_zalando:
            return _r(self.vk_zalando / Decimal("1.19") - self.vk_zalando)

    @property
    def generic_costs(self):  # H2
        """Generic costs =SUM(C2*1,03-C2)"""
        if self.vk_zalando:
            return _r(self.vk_zalando * Decimal("1.03") - self.vk_zalando)

    @property
    def profit_after_taxes(self):  # I2
        """=SUM(C2-B2-D2+F2+G2+H2)"""
        if self.vk_zalando:
            base = self.vk_zalando - self.costs_production - self.shipping_costs
            return _r(
                base
                + self.eight_percent_provision
                + self.nineteen_percent_vat
                + self.generic_costs
            )

    @property
    def category_name(self):
        """Return the name of the category."""
        if self.category:
            return self.category.name
        return "N/A"

    @property
    def total_revenue(self):
        """Revenue from all sold items."""
        if self.vk_zalando:
            return self.profit_after_taxes * (self.shipped - self.returned)
        return 0

    @property
    def total_return_costs(self):
        """Return costs (plus schmalz) from all returned items."""
        if self.vk_zalando:
            return self.returned * (
                self.shipping_costs + self.return_costs + self.generic_costs
            )
        return 0

    def total_diff(self):
        """..."""
        return self.total_revenue - self.total_return_costs


class ZCost(TimeStampedModel):
    """Control for zalando specific prices."""

    shipping = models.DecimalField(max_digits=6, decimal_places=2)
    returnc = models.DecimalField(max_digits=6, decimal_places=2)

    def save(self, *args, **kwargs):
        super(ZCost, self).save(*args, **kwargs)

        ZProduct.objects.all().update(
            return_costs=self.returnc, shipping_costs=self.shipping
        )


class RawDailyShipmentReport(TimeStampedModel):
    """Relevant data from daily shipment reports from Zalando."""

    price = models.ForeignKey("core.Price", on_delete=models.PROTECT)
    article_number = models.CharField(max_length=32)
    cancel = models.BooleanField(default=False)
    channel_order_number = models.CharField(max_length=16)
    order_created = models.DateTimeField()
    order_event_time = models.DateTimeField()
    price_in_cent = models.PositiveIntegerField()
    return_reason = models.CharField(max_length=256)
    returned = models.BooleanField(default=False)
    shipment = models.BooleanField(default=False)
    marketplace_config = models.ForeignKey(
        "core.MarketplaceConfig", on_delete=models.PROTECT, blank=True, null=True
    )

    class Meta:
        db_table = "zalando_dailyshipmentreport_raw"


class SalesReportFileUpload(TimeStampedModel):
    """Upload of CSV files which contain monthly sales reports."""

    processed = models.BooleanField(default=False)
    original_csv = models.FileField(
        upload_to="zalando/finance/monthly_sales_reports",
        max_length=128,
    )
    file_name = models.CharField(max_length=128, unique=True)

    def __repr__(self):
        return f"SalesReportFileUploadFile({self.original_csv})"

    class Meta:
        db_table = "zalando_monthly_sales_report_file_upload"


class SalesReport(TimeStampedModel):
    """Data from monthly sales reports from Z."""

    class Currency(models.TextChoices):
        EUR = "EUR", "Euro"

    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.EUR
    )
    ean = models.CharField(max_length=13)
    order_date = models.DateTimeField()
    order_number = models.BigIntegerField()
    pai_fee = models.DecimalField(max_digits=8, decimal_places=2)
    payment_service_fee = models.DecimalField(max_digits=8, decimal_places=2)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    shipment_subtype = models.CharField(max_length=32)  # Enum?
    shipment_type = models.CharField(max_length=32)  # Enum?
    shipping_return_date = models.DateTimeField()

    import_reference = models.ForeignKey(
        SalesReportFileUpload,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    zalando_marketplace_config = models.ForeignKey(
        "core.MarketplaceConfig", on_delete=models.PROTECT, blank=True, null=True
    )

    class Meta:
        db_table = "zalando_monthly_sales_report"

    @property
    def price_as_str(self):
        return str(self.price).replace(".", ",")

    @property
    def shipment(self):
        return self.shipment_type == "Sale"

    @property
    def all_fees_as_str(self):
        result = self.pai_fee + self.payment_service_fee
        return str(result).replace(".", ",")
