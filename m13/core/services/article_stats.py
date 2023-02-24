import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from django.db import connection

from core.models import MarketplaceConfig
from m13.lib.psql import dictfetchall

LOG = logging.getLogger(__name__)


class Marketplace(StrEnum):
    OTTO = "OTTO"
    ZALANDO = "ZALANDO"


def _r(value):
    """Return rounded value."""
    return round(value, 2)


@dataclass
class ArticleStats:
    """..."""

    sku: str
    category: str
    marketplace: Marketplace

    price: Decimal
    provision_in_percent: Decimal

    vat_in_percent: int
    generic_costs_in_percent: int

    production_costs: Decimal
    shipping_costs: Decimal
    return_costs: Decimal

    shipped: int = 0
    returned: int = 0
    canceled: int = 0

    @property
    def provision_amount(self):
        """Return the amount of the provision depending on price and provision."""
        return _r(self.price * self.provision_in_percent / 100)

    @property
    def vat_amount(self):
        """Return the amount of the vat (aka 'Märchensteuer')."""
        return _r(self.price * self.vat_in_percent / 100)

    @property
    def generic_costs_amount(self):
        """Return the amount of the generic costs for the article."""
        return _r(self.price * self.generic_costs_in_percent / 100)

    @property
    def profit_after_taxes(self):
        """Return the actual profit after substracting all costs and taxes."""
        try:
            return _r(
                self.price
                - self.production_costs
                - self.shipping_costs
                - self.provision_amount
                - self.vat_amount
                - self.generic_costs_amount
            )
        except TypeError:
            LOG.error(f"Missing information for {self.sku}")
            LOG.error(self)
            # import ipdb; ipdb.set_trace()
            return 0

    @property
    def total_revenue(self):
        """Revenue from all sold items."""
        return self.profit_after_taxes * (self.shipped - self.returned)

    @property
    def total_return_costs(self):
        """Return costs (plus schmalz) from all returned items."""
        return self.returned * (
            self.shipping_costs + self.return_costs + self.generic_costs_amount
        )

    @property
    def total_diff(self):
        """..."""
        return self.total_revenue - self.total_return_costs

    @property
    def sales(self):
        """Return amount which was generated due to sales."""
        return self.price * self.shipped


def get_article_stats_otto(start_date: date) -> dict:
    """Return orderitem statistics for marketplace otto."""
    LOG.info(f"get_article_stats_otto called with start_date: {start_date}")
    return {}


def get_z_provision_in_percent(price: Decimal) -> Decimal:
    """Return the amount of provision for zalando."""
    # Payment Service Fee
    payment_service_fee = Decimal("1.55")
    # plus Platform & Integration Fee (depending on price)
    # if price is lower than 50 bugs the fucktor is 3.55
    pi_fee = Decimal("3.55")

    if price > Decimal("50") and price <= Decimal("80"):
        pi_fee = Decimal("8.55")
    elif price > Decimal("80") and price <= Decimal("80"):
        pi_fee = Decimal("13.55")
    elif price > Decimal("120"):
        pi_fee = Decimal("13.55")

    return payment_service_fee + pi_fee


def get_article_stats_zalando(start_date: date) -> dict:
    """Return dictionary with aggregated values for number of shipped, returned and canceled."""
    LOG.info(f"get_article_stats_zalando - start_date: {start_date}")

    try:
        config = MarketplaceConfig.objects.get(name=Marketplace.ZALANDO, active=True)
    except MarketplaceConfig.DoesNotExist:
        LOG.exception("No marketplace config found for zalando")
        return {}

    result = {}
    params = {"start_date": start_date}
    with connection.cursor() as cursor:
        query = """
            SELECT
                cc.name as category_name,
                cp.sku as sku,
                cp.costs_production as costs_production,
                zdr.price_in_cent as reported_price,
                COALESCE(SUM(zdr.price_in_cent) FILTER (WHERE zdr.shipment), 0) AS sum_shipped,
                COALESCE(SUM(zdr.price_in_cent) FILTER (WHERE zdr.returned), 0) AS sum_returned,
                COALESCE(SUM(zdr.price_in_cent) FILTER (WHERE zdr.cancel), 0) AS sum_canceled,
                COUNT(zdr.shipment) FILTER (WHERE zdr.shipment) AS shipped,
                COUNT(zdr.returned) FILTER (WHERE zdr.returned) AS returned,
                COUNT(zdr.cancel) FILTER (WHERE zdr.cancel) AS canceled
            FROM
                zalando_dailyshipmentreport_raw AS zdr
            JOIN core_price AS cp
                ON cp.sku = zdr.article_number
            JOIN core_category AS cc
                on cc.id = cp.category_id
            WHERE
                order_event_time >= %(start_date)s
                AND article_number <> ''
            GROUP BY
                category_name, sku, reported_price
            ORDER BY
                sku, reported_price DESC
        """
        cursor.execute(query, params)
        for entry in dictfetchall(cursor):

            category = entry["category_name"]
            price = _r(Decimal(entry["reported_price"] / 100))
            provision_in_percent = get_z_provision_in_percent(price)

            astats = ArticleStats(
                sku=entry["sku"],
                category=category,
                marketplace=Marketplace.ZALANDO,
                price=price,
                provision_in_percent=provision_in_percent,
                vat_in_percent=config.vat_in_percent,
                generic_costs_in_percent=config.generic_costs_in_percent,
                production_costs=entry["costs_production"],
                shipping_costs=config.shipping_costs,
                return_costs=config.return_costs,
                shipped=entry["shipped"],
                returned=entry["returned"],
                canceled=entry["canceled"],
            )
            if category not in result:
                result[category] = {
                    "content": [],
                    "name": category,
                    "stats": {
                        "canceled": 0,
                        "returned": 0,
                        "sales": 0,
                        "shipped": 0,
                        "total_diff": 0,
                        "total_return_costs": 0,
                        "total_revenue": 0,
                    },
                }

            result[category]["content"].append(
                {
                    "article_number": astats.sku,
                    "canceled": astats.canceled,
                    "category": astats.category,
                    "costs_production": astats.production_costs,
                    "eight_percent_provision": astats.provision_amount,
                    "generic_costs": astats.generic_costs_amount,
                    "nineteen_percent_vat": astats.vat_amount,
                    "profit_after_taxes": astats.profit_after_taxes,
                    "return_costs": astats.return_costs,
                    "returned": astats.returned,
                    "sales": astats.sales,
                    "shipped": astats.shipped,
                    "shipping_costs": astats.shipping_costs,
                    "total_diff": astats.total_diff,
                    "total_return_costs": astats.total_return_costs,
                    "total_revenue": astats.total_revenue,
                    "vk_zalando": astats.price,
                }
            )
            result[category]["stats"]["canceled"] += astats.canceled
            result[category]["stats"]["sales"] += astats.sales
            result[category]["stats"]["shipped"] += astats.shipped
            result[category]["stats"]["returned"] += astats.returned
            result[category]["stats"]["total_revenue"] += astats.total_revenue
            result[category]["stats"]["total_return_costs"] += astats.total_return_costs
            result[category]["stats"]["total_diff"] += astats.total_diff

    return result


def get_article_stats(start_date: date, marketplace: Marketplace) -> dict:
    """Return list of marketplace dependent statistics about shipments/returns."""
    LOG.info(f"marketplace: {marketplace} start_date: {start_date}")

    match (marketplace.upper()):
        case Marketplace.OTTO:
            return get_article_stats_otto(start_date)
        case Marketplace.ZALANDO:
            return get_article_stats_zalando(start_date)
        case _:
            LOG.error(f"get_article_stats with unknown marketplace: {marketplace}")
            return {}
