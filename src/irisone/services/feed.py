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

from core.models import Price
from irisone.models import FeedUpload
from zalando.constants import SKU_BLACKLIST
from zalando.models import PriceTool

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
    "user-agent": "manufaktur13",
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
    "erp_article_location",
    "classification",
]


# ---------------------------------------------------------------------------
# Pricing rules — kept in sync with zalando/services/feed.py.
# Duplicated (not imported) because importing zalando.services.feed runs
# module-level code that calls sys.exit() when Zalando env vars are missing.
# ---------------------------------------------------------------------------

SHIPPING_FEE = 3.95

PRICES = [
    14.95,
    17.95,
    19.95,
    24.95,
    27.95,
    29.95,
    34.95,
    37.95,
    39.95,
    44.95,
    47.95,
    49.95,
    54.95,
    59.95,
    64.95,
    69.95,
    74.95,
    79.95,
    84.95,
    89.95,
    99.95,
    104.95,
    109.95,
    114.95,
    119.95,
    124.95,
    129.95,
    132.95,
    134.95,
    139.95,
    144.95,
    149.95,
    154.95,
    159.95,
    164.95,
    169.95,
    174.95,
    179.95,
    184.95,
    189.95,
    199.95,
]

price_overwrites = [
    ("26.95", "29.95", "FB-21"),
    ("26.95", "29.95", "ds-beanie-mu"),
    ("26.95", "29.95", "ds-beanie-vi"),
    ("26.95", "29.95", "ds-beanie-na"),
    ("26.95", "29.95", "BM012"),
    ("26.95", "29.95", "BM017-FBM"),
    ("26.95", "29.95", "BM022"),
    ("26.95", "29.95", "BM0002"),
    ("26.95", "29.95", "BM020"),
    ("26.95", "29.95", "BM0003"),
    ("26.95", "29.95", "FB-07-FBM"),
    ("26.95", "29.95", "HDB-08"),
    ("26.95", "29.95", "FB-06"),
    ("26.95", "29.95", "HDB-02-FBM"),
    ("26.95", "29.95", "HDB-07-FBM"),
    ("26.95", "29.95", "HDB-04-FBM"),
    ("26.95", "29.95", "HDB-03-FBM"),
    ("26.95", "29.95", "HKB-001"),
    ("26.95", "29.95", "HKB-002"),
    ("26.95", "29.95", "HKB-003"),
    ("26.95", "29.95", "HKB-004"),
    ("26.95", "29.95", "HKB-005"),
    ("26.95", "29.95", "HKB-006"),
    ("26.95", "29.95", "HKB-007"),
    ("26.95", "29.95", "HKB-008"),
    ("26.95", "29.95", "SM001"),
    ("26.95", "29.95", "SM002"),
    ("26.95", "29.95", "SM003"),
    ("26.95", "29.95", "SM004"),
    ("26.95", "29.95", "SM005"),
    ("26.95", "29.95", "SM006"),
    ("26.95", "29.95", "SM007"),
    ("26.95", "29.95", "SM008"),
    ("52.95", "59.95", "Knit-Set-AS"),
    ("52.95", "59.95", "Knit-Set-MU"),
    ("52.95", "59.95", "Knit-Set-NA"),
    ("52.95", "59.95", "Knit-Set-BL"),
    ("29.95", "34.95", "KB007"),
    ("29.95", "34.95", "KB008"),
    ("29.95", "34.95", "KB009"),
    ("29.95", "34.95", "KB010"),
    ("48.95", "54.95", "FWIN-SET-NA"),
    ("29.95", "34.95", "RKS001"),
    ("29.95", "34.95", "RKS004"),
    ("62.95", "69.95", "HoodedLoop018"),
    ("57.95", "64.95", "KLOOP-GS"),
    ("57.95", "64.95", "KLOOP-NA"),
    ("57.95", "64.95", "KLOOP-OL"),
    ("42.95", "47.95", "KWINDBR-TU"),
    ("29.95", "34.95", "Windbreaker-001"),
    ("29.95", "34.95", "Windbreaker-003"),
    ("42.95", "47.95", "KWINDBR-MU"),
    ("42.95", "47.95", "KWINDBR-BX"),
    ("42.95", "47.95", "KWINDBR-RO"),
    ("42.95", "47.95", "KWINDBR-NA"),
    ("42.95", "47.95", "KWINDBR-OL"),
    ("26.95", "29.95", "NECKW-OL"),
    ("62.95", "69.95", "HoodedLoop006"),
    ("62.95", "69.95", "HoodedLoop017"),
    ("62.95", "69.95", "HoodedLoop007"),
    ("62.95", "69.95", "HoodedLoop014"),
    ("52.95", "59.95", "duffel-sand"),
    ("52.95", "59.95", "duffel-greymat"),
    ("52.95", "59.95", "duffel-asphalt"),
    ("52.95", "59.95", "CBBDuffle-DG"),
    ("52.95", "59.95", "CBBDuffle-NA"),
    ("52.95", "59.95", "CBBDuffle-OL"),
    ("44.95", "49.95", "SportsBag25-FBM"),
]

extra_worst_for_out_of_season_article = {
    "women-bom-co-xs": {
        "fake_sku": "women-bom-co-xs-1",
        "fake_ean": "9501796764646",
    },
    "women-bom-co-s": {
        "fake_sku": "women-bom-co-s-1",
        "fake_ean": "9509454376477",
    },
    "women-bom-co-m": {
        "fake_sku": "women-bom-co-m-1",
        "fake_ean": "9508355589344",
    },
    "women-bom-co-l": {
        "fake_sku": "women-bom-co-l-1",
        "fake_ean": "9508169288839",
    },
    "women-bom-co-xl": {
        "fake_sku": "women-bom-co-xl-1",
        "fake_ean": "9501138142941",
    },
}


class IrisOneFeedException(Exception):
    pass


def _get_price(price, factor):
    """Return beautiful price after factor was applied."""
    price = round(price * factor, 2) + SHIPPING_FEE

    while True:
        price = round(price + 0.01, 2)
        if price in PRICES:
            return price

        if price > 200:
            # This should never happen
            return "ERROR"


def _get_z_factor():
    """Return the active Zalando price factor (shared with the Zalando feed)."""
    try:
        price_tool = PriceTool.objects.get(active=True)
    except PriceTool.DoesNotExist:
        raise IrisOneFeedException("No price factor found")
    return float(price_tool.z_factor)


def _build_overwrites():
    """Index the hardcoded price overwrites by SKU."""
    return {
        sku: {"price": price, "retail_price": retail_price}
        for price, retail_price, sku in price_overwrites
    }


def _resolve_price(article_number, shop_price, factor, overwrites):
    """Resolve (price, retail_price) using the Zalando pimping rules.

    Precedence: pimped_zalando flag (hard vk_zalando) > computed factor price;
    price_overwrites win over both. retail_price defaults to price.
    """
    try:
        core_price = Price.objects.get(sku__iexact=article_number, pimped_zalando=True)
        price = core_price.vk_zalando
    except Price.DoesNotExist:
        price = _get_price(float(shop_price.replace(",", ".")), factor)

    retail_price = price
    if article_number in overwrites:
        price = overwrites[article_number]["price"]
        retail_price = overwrites[article_number]["retail_price"]

    return str(price), str(retail_price)


def _clamp_quantity(raw):
    """Empty quantity becomes 0; negative quantity is clamped to 0."""
    if raw == "":
        return "0"
    try:
        return "0" if int(raw) < 0 else raw
    except ValueError:
        return raw


def _out_of_season_rows(article_number):
    """Return fake (ean, sku) duplicates for out-of-season articles."""
    extra = extra_worst_for_out_of_season_article.get(article_number)
    if not extra:
        return []
    return [(extra["fake_ean"], extra["fake_sku"])]


def download_shop_feed():
    """Download the raw shop CSV feed and return it as list of rows."""
    if not IRISONE_FEED_PATH:
        raise IrisOneFeedException("Missing environment variable IRISONE_FEED_PATH")

    LOG.info(f"GET {IRISONE_FEED_PATH}")
    response = requests.get(IRISONE_FEED_PATH, timeout=60)
    response.raise_for_status()

    decoded = response.content.decode("utf-8")
    reader = csv.reader(decoded.splitlines(), delimiter=";")
    return list(reader)


def _build_irisone_csv(shop_rows, output_path):
    """Transform shop feed rows into irisOne CSV format.

    Expected shop feed columns (semicolon-separated):
      store ; ean ; price ; retail_price ; quantity ; article_number ; ...

    Pricing follows the same rules as the Zalando pimped feed: blacklisted
    SKUs and rows without ean/article_number are dropped, price/retail_price
    are derived via _resolve_price, and out-of-season articles are duplicated.
    """
    factor = _get_z_factor()
    overwrites = _build_overwrites()

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
            article_number = row[5]

            if not article_number or not ean:
                continue
            if article_number in SKU_BLACKLIST:
                LOG.debug(f"SKU {article_number} black listed")
                continue

            price, retail_price = _resolve_price(
                article_number, row[2], factor, overwrites
            )
            quantity = _clamp_quantity(row[4])

            writer.writerow([store, ean, article_number, price, retail_price, quantity])
            count += 1

            for fake_ean, fake_sku in _out_of_season_rows(article_number):
                writer.writerow(
                    [store, fake_ean, fake_sku, price, retail_price, quantity]
                )
                count += 1

    LOG.info(f"irisOne CSV written: {output_path} ({count} items)")
    return count


def _build_irisone_product_csv(shop_rows, output_path):
    """Transform shop feed into irisOne product data CSV.

    All shop feed columns are included, plus 4 ERP mapping columns:
    erp_ean, erp_article_number, erp_article_location, classification.

    Pricing follows the same rules as the Zalando pimped feed: blacklisted
    SKUs and rows without ean/article_number are dropped, price/retail_price
    are derived via _resolve_price, and out-of-season articles are duplicated.
    """
    factor = _get_z_factor()
    overwrites = _build_overwrites()

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
            article_number = row[5]
            article_color = row[6] if len(row) > 6 else ""
            product_name = row[7] if len(row) > 7 else ""
            store_article_location = row[8] if len(row) > 8 else ""
            product_number = row[9] if len(row) > 9 else ""
            article_size = row[10] if len(row) > 10 else ""

            if not article_number or not ean:
                continue
            if article_number in SKU_BLACKLIST:
                LOG.debug(f"SKU {article_number} black listed")
                continue

            price, retail_price = _resolve_price(
                article_number, row[2], factor, overwrites
            )
            quantity = _clamp_quantity(row[4])

            # original row plus any out-of-season duplicates (fake ean/sku)
            for row_ean, row_sku in [(ean, article_number)] + _out_of_season_rows(
                article_number
            ):
                writer.writerow(
                    [
                        store,
                        row_ean,
                        price,  # price (pimped)
                        retail_price,  # retail_price (pimped)
                        quantity,
                        row_sku,
                        article_color,
                        product_name,
                        store_article_location,
                        product_number,
                        article_size,
                        row_ean,  # erp_ean
                        row_sku,  # erp_article_number
                        store_article_location,  # erp_article_location
                        "default",  # classification
                    ]
                )
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
        f"{IRISONE_API_BASE_URL}/quickConnect/productImport/import_full_{timestamp}.csv"
    )

    LOG.info(f"PUT {url}")
    with open(output_path, "rb") as f:
        response = requests.put(url, headers=HEADERS, data=f.read(), timeout=120)

    LOG.info(f"PUT {url} -> {response.status_code}")

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

    LOG.info(f"PUT {url}")
    with open(output_path, "rb") as f:
        response = requests.put(url, headers=HEADERS, data=f.read(), timeout=120)

    LOG.info(f"PUT {url} -> {response.status_code}")

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
