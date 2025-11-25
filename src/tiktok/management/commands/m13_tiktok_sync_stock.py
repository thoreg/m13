import logging
import os

from django.core.management.base import BaseCommand

from tiktok.lib import download_feed
from tiktok.services.stock import StockService

M13_TIKTOK_FEED = os.getenv("M13_TIKTOK_FEED")


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        #
        # ( 0 ) Basic things work ...
        #
        # ss = StockService()
        # # ss.get_products(refresh=True)
        # ss.get_products()
        # for product in Product.objects.all():
        #     ss.update_inventory(product.seller_sku, 99)

        #
        # ( 1 ) Sync from file ...
        #
        # ss = StockService()
        # with open("tiktokshop.csv", "r") as csvfile:
        #     spamreader = csv.DictReader(csvfile, delimiter=";")
        #     for row in spamreader:
        #         sku = row["Verkäufer-SKU"]
        #         quantity = row["Menge in DE Pickup Warehouse"]
        #         ss.update_inventory(sku, int(quantity))

        #
        # ( 2 ) Sync from url ...
        #
        if not M13_TIKTOK_FEED:
            LOG.error("M13_TIKTOK_FEED not defined")
            return

        ss = StockService()

        # Check if there are new products upstream -> create local db entries
        # with all kind of tiktok ids (product_id, warehouse_id, sku_id)
        ss.get_products()

        # Download the feed and sync the inventory with tiktok
        for row in download_feed(M13_TIKTOK_FEED):
            sku = row["Verkäufer-SKU"]
            quantity = row["Menge in DE Pickup Warehouse"]
            ss.update_inventory(sku, int(quantity))
