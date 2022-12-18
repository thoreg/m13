import csv
import logging
import os
import sys
from typing import NamedTuple

import requests
from django.conf import settings

from m13.common import now_as_str
from zalando.constants import SKU_BLACKLIST
from zalando.models import FeedUpload, PriceTool, Product, ZProduct

LOG = logging.getLogger(__name__)

ZALANDO_FEED_PATH = os.getenv("ZALANDO_M13_FEED")
ZALANDO_API_KEY = os.getenv("ZALANDO_API_KEY")
ZALANDO_CLIENT_ID = os.getenv("ZALANDO_CLIENT_ID")
ZALANDO_VALIDATION_URL = (
    f"https://merchants-connector-importer.zalandoapis.com/{ZALANDO_CLIENT_ID}/validate"
)

FEED_NAME = f"{now_as_str()}.csv"
ZALANDO_FEED_URL = f"https://merchants-connector-importer.zalandoapis.com/{ZALANDO_CLIENT_ID}/{FEED_NAME}"

if not all([ZALANDO_CLIENT_ID, ZALANDO_API_KEY]):
    print("\ncheck you environment variables - do you what you are doing son?\n")
    sys.exit(1)

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

FACTOR = None
SHIPPING_FEE = 3.95

HEADERS = {
    "x-api-key": ZALANDO_API_KEY,
    "content-type": "application/csv",
    "cache-control": "no-cache",
}


def _get_price(price, factor):
    """Return beautiful price after factor was applied."""
    price = round(price * factor, 2) + SHIPPING_FEE

    while True:
        # print(price)
        price = round(price + 0.01, 2)
        if price in PRICES:
            return price

        if price > 200:
            # This should never happen
            return "ERROR"


class DtoZalandoFeed(NamedTuple):
    """Data transfer object."""

    lines: list
    no_ean: int
    no_quantity: int
    number_of_valid_items: int
    path_origin_feed: str


class ZalandoException(Exception):
    pass


def download_feed():
    """Download feed from M13 shop and return list of stock."""
    if not ZALANDO_FEED_PATH:
        raise ZalandoException("Missing Environment Variable ZALANDO_FEED_PATH")

    try:
        response = requests.get(ZALANDO_FEED_PATH)
        decoded_content = response.content.decode("utf-8")
        cr = csv.reader(decoded_content.splitlines(), delimiter=";")
        return list(cr)
    except IndexError:
        raise ZalandoException("IndexError - is the feed available in the shop?")
    except Exception as exc:
        raise exc


def save_original_feed(csv_content_as_list):
    """Download the original stock+price feed from M13 shop."""
    lines = []
    meta = {"no_ean": 0, "no_quantity": 0}

    path_origin_feed = os.path.join(
        settings.MEDIA_ROOT, "original", f"{now_as_str()}.csv"
    )

    with open(path_origin_feed, "w", encoding="UTF8") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        for idx, row in enumerate(csv_content_as_list):
            #
            # ROW is [
            #   'store', 'ean', 'price', 'retail_price', 'quantity',
            #   'article_number', 'article_color', 'product_name',
            #   'store_article_location', 'product_number', 'article_size']
            # import ipdb; ipdb.set_trace()
            #
            if row[1] == "":
                # print(f'SKIP LINE No {idx} - no ean - {row[5]} - {row[7]}')
                meta["no_ean"] += 1
                continue

            if row[5] in SKU_BLACKLIST:
                print(f"SKU {row[5]} black listed")
                continue

            if row[4] == "":
                print(f"LINE No {idx} - no quantity - {row[7]}")
                meta["no_quantity"] += 1
                row[4] = 0

            writer.writerow(row)
            lines.append(row)

    LOG.info(f"Houston we have a csv with {len(lines)} lines")
    LOG.info(f"Origin feed: {path_origin_feed}")
    return DtoZalandoFeed(
        lines=lines,
        no_ean=meta["no_ean"],
        no_quantity=meta["no_quantity"],
        number_of_valid_items=len(lines),
        path_origin_feed=path_origin_feed,
    )


def pimp_prices(lines):
    """Apply pricing algorithm and write out pimped feed."""
    global FACTOR

    def get_z_factor():
        price_tool = PriceTool.objects.get(active=True)
        if not price_tool:
            raise ZalandoException("No Base Price Found")

        return float(price_tool.z_factor)

    try:
        FACTOR = get_z_factor()
    except PriceTool.DoesNotExist:
        LOG.error("No price factor found")
        raise ZalandoException("No price factor found")

    if not lines:
        raise ZalandoException("No feed found")

    for row in lines[1:]:
        # print(row)
        # 2 price
        # 3 retail_price
        # 7 name

        try:
            # Special overwrite on certain products - just take hard the vk_zalando
            # without further any further modification
            zproduct = ZProduct.objects.get(article=row[5], pimped=True)
            price = zproduct.vk_zalando

        except ZProduct.DoesNotExist:
            _price = float(row[2].replace(",", "."))
            price = _get_price(_price, FACTOR)

        ean = row[1]
        retail_price = price
        product_name = row[7]
        LOG.debug(f"{product_name}: {row[2]} -> {price}")
        Product.objects.get_or_create(ean=ean, defaults={"title": product_name})
        row[2] = str(price)
        row[3] = str(retail_price)

    pimped_file_name = os.path.join(
        settings.MEDIA_ROOT, "pimped", f"{now_as_str()}.csv"
    )
    with open(pimped_file_name, "w", encoding="UTF8") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        for row in lines:
            writer.writerow(row)

    LOG.info(f"{pimped_file_name} written")
    return pimped_file_name


def validate_feed(file_name):
    """Ask Z for validation of the feed."""
    with open(file_name, "rb") as f:
        resp = requests.put(ZALANDO_VALIDATION_URL, headers=HEADERS, data=f.read())

    LOG.info(f"Response code (validation): {resp.status_code}")
    # LOG.info(resp.json())
    if resp.status_code != requests.codes.ok:
        LOG.error("Got other than 200")
        LOG.error(resp.json())
        raise ZalandoException("Feed is not valid")

    return resp.status_code


def upload_pimped_feed(pimped_file_name, status_code_validation, dto):
    """..."""
    global FACTOR

    assert FACTOR is not None

    with open(pimped_file_name, "rb") as f:
        resp = requests.put(ZALANDO_FEED_URL, headers=HEADERS, data=f.read())

    # Response is empty - b''
    LOG.info(f"Response code (feed): {resp.status_code}")
    status_code_feed_upload = resp.status_code
    if resp.status_code != requests.codes.ok:
        LOG.error("Got other than 200")
        LOG.error(resp.json())
        raise ZalandoException("Upload Failed")

    fupload = FeedUpload(
        status_code_validation=status_code_validation,
        status_code_feed_upload=status_code_feed_upload,
        number_of_valid_items=dto.number_of_valid_items,
        path_to_original_csv=dto.path_origin_feed,
        path_to_pimped_csv=pimped_file_name,
        z_factor=FACTOR,
    )
    fupload.save()
