import csv
import logging
import os

import pandas as pd
import requests
from attr import dataclass
from django.conf import settings

from galeria.models import FeedUpload
from m13.common import now_as_str

LOG = logging.getLogger(__name__)

GALERIA_FEED_PATH = os.getenv("M13_GALERIA_FEED_PATH")

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

FACTOR = 1.2
SHIPPING_FEE = 3.95


class GaleriaException(Exception):
    pass


@dataclass
class GaleriaFeed:
    lines: list
    path_origin_feed: str


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


def download_feed():
    """Download feed from M13 shop and return list of stock and prices."""
    if not GALERIA_FEED_PATH:
        raise GaleriaException("Missing Environment Variable M13_GALERIA_FEED_PATH")

    try:
        response = requests.get(GALERIA_FEED_PATH)
        decoded_content = response.content.decode("utf-8")
        cr = csv.reader(decoded_content.splitlines(), delimiter=";")
        return list(cr)
    except IndexError:
        raise GaleriaException("IndexError - is the feed available in the shop?")
    except Exception as exc:
        raise exc


def save_original_feed(csv_content_as_list):
    """Save the original stock+price feed for Galeria."""
    lines = []
    path_origin_feed = os.path.join(
        settings.MEDIA_ROOT, "original", "galeria", f"{now_as_str()}.galeria.csv"
    )

    with open(path_origin_feed, "w", encoding="UTF8") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        for idx, row in enumerate(csv_content_as_list):
            #
            # ROW is [
            #   'GTIN', 'Bestand', 'Lieferzeit', 'Einkaufspreis',
            #   'Verkaufsspreis', 'Aktionspreis', 'Gültigkeit bis']
            #
            # if row[4] == "":
            #     LOG.debug(f"LINE No {idx} - no quantity - {row[7]}")
            #     meta["no_quantity"] += 1
            #     row[4] = 0
            writer.writerow(row)
            lines.append(row)

    LOG.info(f"Houston we have a csv with {len(lines)} lines")
    LOG.info(f"Origin feed: {path_origin_feed}")
    return GaleriaFeed(
        lines=lines,
        path_origin_feed=path_origin_feed,
    )


def pimp_prices(lines):
    """Apply pricing algorithm and write out pimped feed."""

    if not lines:
        raise GaleriaException("No feed found")

    for row in lines[1:]:
        # print(row)
        # ['GTIN', 'Bestand', 'Lieferzeit', 'Einkaufspreis', 'Verkaufsspreis',
        #  'Aktionspreis', 'Gültigkeit bis']
        # ['0781491972020', '5', '', '', '49.95', '', '']
        # 0 sku/ean/thing
        # 1 quantity
        # 4 price

        sku = row[0]
        _price = float(row[4].replace(",", "."))
        price = _get_price(_price, FACTOR)

        LOG.debug(f"{sku} : {row[4]} -> {price}")

        row[4] = str(price)

    pimped_file_name = os.path.join(
        settings.MEDIA_ROOT, "pimped", "galeria", f"{now_as_str()}.galeria.csv"
    )
    with open(pimped_file_name, "w", encoding="UTF8") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        for row in lines:
            writer.writerow(row)
    LOG.info(f"{pimped_file_name} written")

    read_file = pd.read_csv(pimped_file_name, sep=";")
    pimped_file_xlsx_name = os.path.join(
        settings.MEDIA_ROOT, "pimped", "galeria", f"{now_as_str()}.galeria.xlsx"
    )
    read_file.to_excel(pimped_file_xlsx_name, index=False, header=True)
    LOG.info(f"{pimped_file_xlsx_name} written")
    return pimped_file_name, pimped_file_xlsx_name


def save_pimped_feed_infos(original_feed_name, pimped_file_name, pimped_file_xlsx_name):
    """Save the paths of the feeds - so they can be downloaded in the frontend."""
    fupload = FeedUpload(
        path_to_original_csv=original_feed_name,
        path_to_pimped_csv=pimped_file_name,
        path_to_pimped_xlsx=pimped_file_xlsx_name,
    )
    fupload.save()
