from django.db import models
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel
from django_pgviews import view as pg


def set_active(instance_id, marketplace_name):
    """Set all other configurations of this marketplace to inactive."""
    MarketplaceConfig.objects.filter(name=marketplace_name).exclude(
        id=instance_id
    ).update(active=False)


class MarketplaceConfig(TimeStampedModel):
    """Marketplace specific configuration of costs."""

    class MarketplaceName(models.TextChoices):
        """Valid marketplace names"""

        OTTO = "OTTO"
        ZALANDO = "ZALANDO"

    name = models.CharField(
        max_length=16, choices=MarketplaceName.choices, default=MarketplaceName.OTTO
    )

    shipping_costs = models.DecimalField(max_digits=5, decimal_places=2)
    """Shipping costs for an article on this marketplace."""
    return_costs = models.DecimalField(max_digits=5, decimal_places=2)
    """Return costs for an article on this marketplace."""
    provision_in_percent = models.IntegerField(blank=True, null=True)
    """Provision per sold item on this marketplace.
       Value can be null when the provision is calculated based on orderitem price.
    """
    vat_in_percent = models.IntegerField(default=19)
    """Value added tax - aka Maerchensteuer."""
    generic_costs_in_percent = models.IntegerField(default=19)
    """Value for average generic costs (like salary, electricity per article."""
    active = models.BooleanField()
    """Flag that indicates, that this configuration is active at the moment.
       When a new configuration is stored, this is set to active automatically.
       There is only one active configuration per marketplace.
    """

    class Meta:
        verbose_name_plural = "Marketplace Configurations"

    def save(self, *args, **kwargs):
        self.active = True
        super(MarketplaceConfig, self).save(*args, **kwargs)
        set_active(self.pk, self.name)


class Category(TimeStampedModel):
    """Product category information."""

    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Price(TimeStampedModel):
    """Central point of price control."""

    sku = models.CharField(max_length=32, primary_key=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.PROTECT)
    costs_production = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    vk_zalando = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    vk_otto = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    pimped_zalando = models.BooleanField(default=False)
    ean = models.CharField(max_length=13, unique=True, null=True, blank=True)
    vk_aboutyou = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return f"{self.category} : {self.sku}"

    def admin_url(self):
        """Return link to the admin interface of the object."""
        url = reverse(
            "admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name),
            args=[self.sku],
        )
        return f"https://m13.thoreg.com{url}"


class Product(TimeStampedModel):
    """DEPRECATED - not in use - just here avoid fixture fuckup."""

    ean = models.CharField(max_length=13, unique=True)
    name = models.CharField(max_length=256)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)


class Article(TimeStampedModel):
    """DEPRECATED - not in use - just here avoid fixture fuckup.

    Solution: remove core.article and all references to it from all fixtures
    Better: Remove all fixtures - they are just causing trouble here and there

    """

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    sku = models.CharField(max_length=32, unique=True)


class Job(TimeStampedModel):
    """Model to keep track of the execution of management commands."""

    cmd = models.CharField(max_length=256)
    description = models.CharField(max_length=256, blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    successful = models.BooleanField(default=False)


class Error(TimeStampedModel):
    """Model to display errors on status page."""

    msg = models.TextField()
    comment = models.CharField(max_length=128, blank=True, null=True)
    cleared = models.BooleanField(default=False)


TOP13_SQL = """
    SELECT
        1 as id,
        cc.name as category_name,
        cp.sku as sku,
        COUNT(1) FILTER ( WHERE msr.shipment_type = 'Sale' ) as shipped

    FROM
        zalando_monthly_sales_report as msr
    JOIN core_price AS cp
        ON cp.ean = msr.ean
    JOIN core_category AS cc
        on cc.id = cp.category_id
    WHERE
        msr.order_date >= '2024-01-01 00:00:00'
        AND msr.order_date <= '2025-01-01 00:00:00'
    GROUP BY
        category_name,
        sku
    ORDER BY shipped DESC
    LIMIT 13;
"""


class SalesStatsTop13(pg.View):
    """Top13 sales by sku.

    Note: not called via api endpoint and viewset -> extra query defined in
          get_queryset()
    """

    sku = models.CharField(max_length=100)
    category_name = models.CharField(max_length=100)
    shipped = models.IntegerField()
    order_date = models.DateTimeField()

    sql = TOP13_SQL

    class Meta:
        """..."""

        db_table = "core_salesstats_top13_view"
        managed = False


TOP13_RETURN_SQL = """
    SELECT
        1 as id,
        cc.name as category_name,
        cp.sku as sku,
        COUNT(1) FILTER ( WHERE msr.shipment_type <> 'Sale' ) as returned

    FROM
        zalando_monthly_sales_report as msr
    JOIN core_price AS cp
        ON cp.ean = msr.ean
    JOIN core_category AS cc
        on cc.id = cp.category_id
    WHERE
        msr.order_date >= '2024-01-01 00:00:00'
        AND msr.order_date <= '2025-01-01 00:00:00'
    GROUP BY
        category_name,
        sku
    ORDER BY returned DESC
    LIMIT 13;
"""


class SalesStatsReturnTop13(pg.View):
    """Top13 return articles by sku.

    Note: not called via api endpoint and viewset -> extra query defined in
          get_queryset()
    """

    sku = models.CharField(max_length=100)
    category_name = models.CharField(max_length=100)
    returned = models.IntegerField()

    sql = TOP13_RETURN_SQL

    class Meta:
        """..."""

        db_table = "core_salesstats_top13_return_view"
        managed = False


SALES_VOLUME_ZALANDO_SQL = """
    SELECT
        1 as id,
        COALESCE(SUM(msr.price) FILTER (WHERE msr.shipment_type = 'Sale'), 0) AS sum_sales,
        msr.order_date::date as day
    FROM
        zalando_monthly_sales_report as msr
    WHERE
        msr.order_date >= '2024-01-01 00:00:00'
        AND msr.order_date <= '2025-01-01 00:00:00'
    GROUP BY
        day
"""


class SalesVolumeZalando(pg.View):
    """Sales volume summed by day.

    Note: not called via api endpoint and viewset -> extra query defined in
          get_queryset()
    """

    sum_sales = models.CharField(max_length=100)
    week = models.CharField(max_length=100)

    sql = SALES_VOLUME_ZALANDO_SQL

    class Meta:
        """..."""

        db_table = "core_sales_volume_zalando_view"
        managed = False
