import csv
import json
import logging
import os
import sys
from dataclasses import dataclass
from typing import NamedTuple

import requests
from django.conf import settings
from django.db.utils import IntegrityError

from core.models import Price
from m13.common import now_as_str
from m13.lib import log as mlog
from zalando.constants import SKU_BLACKLIST
from zalando.models import FeedUpload, PriceTool, Product

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


@dataclass
class Row:
    store: str
    ean: str
    price: str
    retail_price: str
    quantity: int
    article_number: str
    article_color: str
    product_name: str
    store_article_location: str
    product_number: str
    article_size: str


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
            #
            if row[1] == "":
                # print(f'SKIP LINE No {idx} - no ean - {row[5]} - {row[7]}')
                meta["no_ean"] += 1
                continue

            if row[5] in SKU_BLACKLIST:
                LOG.debug(f"SKU {row[5]} black listed")
                continue

            if row[4] == "":
                LOG.debug(f"LINE No {idx} - no quantity - {row[7]}")
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
        mlog.error(LOG, "No price factor found")
        raise ZalandoException("No price factor found")

    if not lines:
        raise ZalandoException("No feed found")

    pimped_lines = []
    # Original order from Z docs:
    # https://docs.partner-solutions.zalan.do/en/fci/getting-started.html
    pimped_lines.append(
        (
            "store",
            "ean",
            "price",
            "retail_price",
            "quantity",
            "product_number",
            "product_name",
            "article_number",
            "article_color",
            "article_size",
            "store_article_location",
        )
    )

    for current_row in lines[1:]:
        # M13
        # "store";"ean";"price";"retail_price";"quantity";"article_number";
        # "article_color";"product_name";"store_article_location";
        # "product_number";"article_size"
        row = Row(
            store=current_row[0],
            ean=current_row[1],
            price=current_row[2],
            retail_price=current_row[3],
            quantity=current_row[4],
            article_number=current_row[5],
            article_color=current_row[6],
            product_name=current_row[7],
            store_article_location=current_row[8],
            product_number=current_row[9],
            article_size=current_row[10],
        )

        try:
            # Special overwrite on certain products - just take hard the vk_zalando
            # without further any further modification
            core_price = Price.objects.get(
                sku__iexact=row.article_number, pimped_zalando=True
            )
            price = core_price.vk_zalando
            LOG.debug(f"{row.article_number} - price via pimped_zalando=True : {price}")

        except Price.DoesNotExist:
            _price = float(row.price.replace(",", "."))
            price = _get_price(_price, FACTOR)
            LOG.debug(f"{row.article_number} - price via _get_price() : {price}")

        LOG.debug(f"{row.article_number} - {row.product_name}: {row.price} -> {price}")

        # Is this still needed? Where is this used?
        Product.objects.get_or_create(ean=row.ean, defaults={"title": row.product_name})

        try:
            # Create new price entries on the fly if EAN is unknown
            _obj, price_created = Price.objects.get_or_create(
                ean=row.ean, defaults={"sku": row.article_number}
            )
            if price_created:
                LOG.info(f"New price entry created: {row.article_number}:{row.ean}")
        except IntegrityError as exc:
            # : duplicate key value violates unique constraint "core_price_pkey"
            # Possible when there is a price with sku but without ean (both values
            # have to be unique)
            str_exc = str(exc)
            if str_exc.startswith("duplicate key value violates unique"):
                # This actually MUST find something
                price = Price.objects.get(sku=row.article_number)
                price.ean = row.ean
                price.save()
                LOG.info(f"EAN added sku: {row.article_number} ean: {row.ean}")

        row.price = str(price)
        row.retail_price = str(price)
        if int(row.quantity) < 0:
            row.quantity = 0

        pimped_lines.append(row)

    pimped_file_name = os.path.join(
        settings.MEDIA_ROOT, "pimped", f"{now_as_str()}.csv"
    )

    # with open(pimped_file_name, "w", encoding="UTF8") as f:
    #     writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    #     for row in lines:
    #         writer.writerow(row)

    with open(pimped_file_name, "w", encoding="UTF8") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        count = 0
        for row in pimped_lines:
            if count == 0:
                writer.writerow(row)
                count += 1
            else:
                resolved_row = (
                    row.store,
                    row.ean,
                    row.price,
                    row.retail_price,
                    row.quantity,
                    row.product_number,
                    row.product_name,
                    row.article_number,
                    row.article_color,
                    row.article_size,
                    row.store_article_location,
                )
                writer.writerow(resolved_row)

    LOG.info(f"{pimped_file_name} written")
    return pimped_file_name


def validate_feed(file_name):
    """Ask Z for validation of the feed."""
    with open(file_name, "rb") as f:
        resp = requests.put(ZALANDO_VALIDATION_URL, headers=HEADERS, data=f.read())

    LOG.info(f"Response code (validation): {resp.status_code}")

    json_response = json.dumps(resp.json())
    LOG.info(json_response)

    if resp.status_code != requests.codes.ok:
        mlog.error(LOG, "Got other than 200")
        mlog.error(LOG, resp.json())
        raise ZalandoException("Feed is not valid")

    # Summarize warnings by line number for lazy chef bosses
    lines = []
    with open(file_name, "r") as f:
        lines = f.readlines()

    result = ""
    resp = json.loads(json_response)
    for warning in resp["warnings"]:
        result += warning["message"]
        result += f" ({warning['details'][0]})\n"
        for ln in warning["line_numbers"]:
            result += lines[ln["line_number"]]
        result += "\n"

    result = result.replace("\n", "<br>")
    return result


def upload_pimped_feed(
    pimped_file_name, status_code_validation, dto, validation_result
):
    """..."""
    global FACTOR

    assert FACTOR is not None

    with open(pimped_file_name, "rb") as f:
        resp = requests.put(ZALANDO_FEED_URL, headers=HEADERS, data=f.read())

    # Response is empty - b''
    LOG.info(f"Response code (feed): {resp.status_code}")
    if resp.status_code != requests.codes.ok:
        mlog.error(LOG, "Got other than 200")
        mlog.error(LOG, resp.json())
        raise ZalandoException("Upload Failed")

    fupload = FeedUpload(
        status_code_validation=status_code_validation,
        status_code_feed_upload=resp.status_code,
        number_of_valid_items=dto.number_of_valid_items,
        path_to_original_csv=dto.path_origin_feed,
        path_to_pimped_csv=pimped_file_name,
        z_factor=FACTOR,
        validation_result=validation_result,
    )
    fupload.save()
