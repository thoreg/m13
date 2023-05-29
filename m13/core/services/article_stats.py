import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from django.db import connection

from m13.lib import log as mlog
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
        return _r(self.price - self.price / Decimal(f"1.{self.vat_in_percent}"))

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
            mlog.error(LOG, f"Missing information for {self.sku} - {self}")
            return 0

    @property
    def total_revenue(self):
        """Revenue from all sold items."""
        result = self.profit_after_taxes * (self.shipped - self.returned)
        if result < 0:
            return Decimal("0.00")
        return result

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


def get_article_stats_otto(start_date: date, end_date: date) -> dict:
    """Return orderitem statistics for marketplace otto."""
    LOG.info(f"get_article_stats_otto called with start_date: {start_date}")

    result = {}
    params = {"start_date": start_date, "end_date": end_date}
    with connection.cursor() as cursor:
        query = """
            SELECT
                cc.name as category_name,
                cp.sku as article_sku,
                cp.costs_production as costs_production,
                oi.price_in_cent as reported_price,
                SUM(case when oi.fulfillment_status = 'SENT' then oi.price_in_cent else 0 end) AS sum_shipped,
                SUM(case when oi.fulfillment_status = 'RETURNED' then oi.price_in_cent else 0 end) AS sum_returned,
                SUM(case when oi.fulfillment_status = 'SENT' then 1 else 0 end) AS shipped,
                SUM(case when oi.fulfillment_status = 'RETURNED' then 1 else 0 end) AS returned,
                config.shipping_costs as shipping_costs,
                config.return_costs as return_costs,
                config.vat_in_percent as vat_in_percent,
                config.generic_costs_in_percent as generic_costs_in_percent
            FROM
                otto_orderitem AS oi
            JOIN otto_order as oo
                ON oo.id = oi.order_id
            JOIN core_price AS cp
                ON cp.sku = oi.sku
            JOIN core_category AS cc
                on cc.id = cp.category_id
            JOIN core_marketplaceconfig AS config
                on config.id = 3
            WHERE
                oo.order_date >= %(start_date)s
                AND oo.order_date <= %(end_date)s
            GROUP BY
                category_name,
                article_sku,
                oi.fulfillment_status,
                reported_price,
                shipping_costs,
                return_costs,
                vat_in_percent,
                generic_costs_in_percent,
                config.id
            HAVING
                (case when oi.fulfillment_status = 'SENT' then 1 else 0 end) > 0
                OR (case when oi.fulfillment_status = 'RETURNED' then 1 else 0 end) > 0
            ORDER BY
                config.id, article_sku, reported_price DESC;
        """
        cursor.execute(query, params)
        for entry in dictfetchall(cursor):
            category = entry["category_name"]
            price = _r(Decimal(entry["reported_price"] / 100))
            provision_in_percent = get_z_provision_in_percent(price)

            astats = ArticleStats(
                sku=entry["article_sku"],
                category=category,
                marketplace=Marketplace.OTTO,
                price=price,
                provision_in_percent=provision_in_percent,
                vat_in_percent=entry["vat_in_percent"],
                generic_costs_in_percent=entry["generic_costs_in_percent"],
                production_costs=entry["costs_production"],
                shipping_costs=entry["shipping_costs"],
                return_costs=entry["return_costs"],
                shipped=entry["shipped"],
                returned=entry["returned"],
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
            result[category]["stats"]["sales"] += astats.sales
            result[category]["stats"]["shipped"] += astats.shipped
            result[category]["stats"]["returned"] += astats.returned
            result[category]["stats"]["total_revenue"] += astats.total_revenue
            result[category]["stats"]["total_return_costs"] += astats.total_return_costs
            result[category]["stats"]["total_diff"] += astats.total_diff

    return result


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


def get_article_stats_zalando(start_date: date, end_date: date) -> dict:
    """Return dictionary with aggregated values for number of shipped, returned and canceled."""
    LOG.info(f"get_article_stats_zalando - start_date: {start_date}")

    result = {}
    params = {"start_date": start_date, "end_date": end_date}
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
                COUNT(zdr.cancel) FILTER (WHERE zdr.cancel) AS canceled,
                config.shipping_costs as shipping_costs,
                config.return_costs as return_costs,
                config.vat_in_percent as vat_in_percent,
                config.generic_costs_in_percent as generic_costs_in_percent

            FROM
                zalando_dailyshipmentreport_raw AS zdr
            JOIN core_price AS cp
                ON cp.sku = zdr.article_number
            JOIN core_category AS cc
                on cc.id = cp.category_id
            JOIN core_marketplaceconfig AS config
                on config.id = zdr.marketplace_config_id
            WHERE
                order_event_time >= %(start_date)s
                AND order_event_time <= %(end_date)s
                AND article_number <> ''
            GROUP BY
                category_name,
                sku,
                reported_price,
                shipping_costs,
                return_costs,
                vat_in_percent,
                generic_costs_in_percent,
                config.id
            HAVING
                COUNT(zdr.shipment) FILTER (WHERE zdr.shipment) > 0
                OR COUNT(zdr.returned) FILTER (WHERE zdr.returned) > 0
            ORDER BY
                config.id, sku, reported_price DESC
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
                vat_in_percent=entry["vat_in_percent"],
                generic_costs_in_percent=entry["generic_costs_in_percent"],
                production_costs=entry["costs_production"],
                shipping_costs=entry["shipping_costs"],
                return_costs=entry["return_costs"],
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


def get_article_stats(
    marketplace: Marketplace, start_date: date, end_date: date
) -> dict:
    """Return list of marketplace dependent statistics about shipments/returns."""
    LOG.info(f"marketplace: {marketplace} start_date: {start_date}")

    match (marketplace.upper()):
        case Marketplace.OTTO:
            return get_article_stats_otto(start_date, end_date)
        case Marketplace.ZALANDO:
            return get_article_stats_zalando(start_date, end_date)
        case _:
            mlog.error(
                LOG, f"get_article_stats with unknown marketplace: {marketplace}"
            )
            return {}
