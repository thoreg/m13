"""irisOne QuickConnect feed upload service.

Downloads the shop stock/price feed and uploads it to irisOne via:
  PUT /quickConnect/productImport/stock_import_{type}_{timestamp}.csv
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
IRISONE_COLUMNS = ["store", "article_number", "price", "retail_price", "quantity"]


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
            price = row[2]
            retail_price = row[3]
            quantity = row[4] if row[4] != "" else "0"
            article_number = row[5]

            if not article_number:
                continue

            writer.writerow([store, article_number, price, retail_price, quantity])
            count += 1

    LOG.info(f"irisOne CSV written: {output_path} ({count} items)")
    return count


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

    feed_upload = FeedUpload.objects.create(
        feed_type=feed_type,
        status_code=response.status_code,
        number_of_items=number_of_items,
        path_to_csv=output_path,
    )

    LOG.info(f"FeedUpload created: {feed_upload.pk}")
    return feed_upload
