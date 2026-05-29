"""irisOne QuickConnect feed upload service.

Stock feed  (every 1h):  PUT /quickConnect/productImport/stock_import_{type}_{timestamp}.csv
Product feed (every 24h): PUT /quickConnect/productImport/import_full_{timestamp}.csv
"""

import csv
import logging
import os

import requests
from django.conf import settings
from django.utils import timezone

from irisone.models import FeedUpload

LOG = logging.getLogger(__name__)

IRISONE_API_KEY = os.getenv("IRISONE_API_KEY", "")
IRISONE_API_BASE_URL = os.getenv(
    "IRISONE_API_BASE_URL", "https://api.io-staging.irisone.io/erp"
)
IRISONE_FEED_PATH = os.getenv("IRISONE_FEED_PATH", "")
IRISONE_STORE_ID = os.getenv("IRISONE_STORE_ID", "default")

HEADERS = {
    "x-api-key": IRISONE_API_KEY,
    "content-type": "text/csv",
}

# Columns expected by irisOne QuickConnect stock import
IRISONE_COLUMNS = [
    "store",
    "ean",
    "article_number",
    "price",
    "retail_price",
    "quantity",
]

# Columns for irisOne product data feed (full shop feed + 4 ERP mapping columns)
IRISONE_PRODUCT_COLUMNS = [
    "store",
    "ean",
    "price",
    "retail_price",
    "quantity",
    "article_number",
    "article_color",
    "product_name",
    "store_article_location",
    "product_number",
    "article_size",
    "erp_ean",
    "erp_article_number",
    "erp_store_article_location",
    "classification",
]


class IrisOneFeedException(Exception):
    pass


def download_shop_feed():
    """Download the raw shop CSV feed and return it as list of rows."""
    if not IRISONE_FEED_PATH:
        raise IrisOneFeedException("Missing environment variable IRISONE_FEED_PATH")

    response = requests.get(IRISONE_FEED_PATH, timeout=60)
    response.raise_for_status()

    decoded = response.content.decode("utf-8")
    reader = csv.reader(decoded.splitlines(), delimiter=";")
    return list(reader)


def _build_irisone_csv(shop_rows, output_path):
    """Transform shop feed rows into irisOne CSV format.

    Expected shop feed columns (semicolon-separated):
      store ; ean ; price ; retail_price ; quantity ; article_number ; ...
    """
    count = 0
    with open(output_path, "w", encoding="UTF-8", newline="") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(IRISONE_COLUMNS)

        for idx, row in enumerate(shop_rows):
            if idx == 0:
                # skip header from shop feed
                continue
            if len(row) < 6:
                LOG.warning(f"Skipping malformed row {idx}: {row}")
                continue

            store = row[0]
            ean = row[1]
            # Shop feed uses German decimal comma; irisOne expects dot.
            # Semantics: shop price = regular retail price → irisOne retail_price
            #            shop retail_price = PP/sale price → irisOne price (fallback to shop price)
            shop_price = row[2].replace(",", ".")
            shop_retail = row[3].replace(",", ".") if row[3] else shop_price
            quantity = row[4] if row[4] != "" else "0"
            article_number = row[5]

            if not article_number or not ean:
                continue

            writer.writerow([store, ean, article_number, shop_retail, shop_price, quantity])
            count += 1

    LOG.info(f"irisOne CSV written: {output_path} ({count} items)")
    return count


def _build_irisone_product_csv(shop_rows, output_path):
    """Transform shop feed into irisOne product data CSV.

    All shop feed columns are included, plus 4 ERP mapping columns:
    erp_ean, erp_article_number, erp_store_article_location, classification.
    """
    count = 0
    with open(output_path, "w", encoding="UTF-8", newline="") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(IRISONE_PRODUCT_COLUMNS)

        for idx, row in enumerate(shop_rows):
            if idx == 0:
                continue
            if len(row) < 6:
                LOG.warning(f"Skipping malformed row {idx}: {row}")
                continue

            store = row[0]
            ean = row[1]
            shop_price = row[2].replace(",", ".")
            shop_retail = row[3].replace(",", ".") if row[3] else shop_price
            quantity = row[4] if row[4] != "" else "0"
            article_number = row[5]
            article_color = row[6] if len(row) > 6 else ""
            product_name = row[7] if len(row) > 7 else ""
            store_article_location = row[8] if len(row) > 8 else ""
            product_number = row[9] if len(row) > 9 else ""
            article_size = row[10] if len(row) > 10 else ""

            if not article_number or not ean:
                continue

            writer.writerow([
                store,
                ean,
                shop_retail,             # price = PP/sale price
                shop_price,              # retail_price = regular price
                quantity,
                article_number,
                article_color,
                product_name,
                store_article_location,
                product_number,
                article_size,
                ean,                     # erp_ean
                article_number,          # erp_article_number
                store_article_location,  # erp_store_article_location
                "default",               # classification
            ])
            count += 1

    LOG.info(f"irisOne product CSV written: {output_path} ({count} items)")
    return count


def upload_product_feed():
    """Generate and upload a product data feed to irisOne (every 24h).

    Returns the created FeedUpload instance.
    """
    if not IRISONE_API_KEY:
        raise IrisOneFeedException("Missing environment variable IRISONE_API_KEY")

    shop_rows = download_shop_feed()

    timestamp = timezone.now().strftime("%Y%m%d%H%M")
    output_dir = os.path.join(settings.MEDIA_ROOT, "irisone", "feeds")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"import_full_{timestamp}.csv")

    number_of_items = _build_irisone_product_csv(shop_rows, output_path)

    url = (
        f"{IRISONE_API_BASE_URL}/quickConnect/productImport/"
        f"import_full_{timestamp}.csv"
    )

    with open(output_path, "rb") as f:
        response = requests.put(url, headers=HEADERS, data=f.read(), timeout=120)

    LOG.info(f"irisOne product feed upload response: {response.status_code} — {url}")

    if response.status_code not in (200, 204):
        LOG.error(f"Upload failed: {response.status_code} {response.text}")
        raise IrisOneFeedException(
            f"Product feed upload failed with status {response.status_code}"
        )

    relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)

    feed_upload = FeedUpload.objects.create(
        feed_type=FeedUpload.FeedType.PRODUCT,
        status_code=response.status_code,
        number_of_items=number_of_items,
        path_to_csv=relative_path,
    )

    LOG.info(f"FeedUpload (product) created: {feed_upload.pk}")
    return feed_upload


def upload_feed(feed_type="full"):
    """Generate and upload a QuickConnect stock/price feed to irisOne.

    Returns the created FeedUpload instance.
    """
    if not IRISONE_API_KEY:
        raise IrisOneFeedException("Missing environment variable IRISONE_API_KEY")

    shop_rows = download_shop_feed()

    timestamp = timezone.now().strftime("%Y%m%d%H%M")
    output_dir = os.path.join(settings.MEDIA_ROOT, "irisone", "feeds")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"stock_import_{feed_type}_{timestamp}.csv")

    number_of_items = _build_irisone_csv(shop_rows, output_path)

    url = (
        f"{IRISONE_API_BASE_URL}/quickConnect/productImport/"
        f"stock_import_{feed_type}_{timestamp}.csv"
    )

    with open(output_path, "rb") as f:
        response = requests.put(url, headers=HEADERS, data=f.read(), timeout=120)

    LOG.info(f"irisOne feed upload response: {response.status_code} — {url}")

    if response.status_code not in (200, 204):
        LOG.error(f"Upload failed: {response.status_code} {response.text}")
        raise IrisOneFeedException(
            f"Feed upload failed with status {response.status_code}"
        )

    relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)

    feed_upload = FeedUpload.objects.create(
        feed_type=feed_type,
        status_code=response.status_code,
        number_of_items=number_of_items,
        path_to_csv=relative_path,
    )

    LOG.info(f"FeedUpload created: {feed_upload.pk}")
    return feed_upload
