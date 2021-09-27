"""Handle feed upload from M13 shop to zalando retailer API endpoint.

Download, transform, validate and upload feed

Run for dry mode:

python manage.py m13_zalando_feed_update --dry

"""
import csv
import io
import logging
import os
import sys
from datetime import datetime
from pprint import pprint

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from m13.common import now_as_str
from zalando.common import get_z_factor
from zalando.models import FeedUpload, Product

LOG = logging.getLogger(__name__)

ZALANDO_FEED_PATH = os.getenv('ZALANDO_M13_FEED')
ZALANDO_API_KEY = os.getenv('ZALANDO_API_KEY')
ZALANDO_CLIENT_ID = os.getenv('ZALANDO_CLIENT_ID')
ZALANDO_VALIDATION_URL = (
    f'https://merchants-connector-importer.zalandoapis.com/{ZALANDO_CLIENT_ID}/validate')

FEED_NAME = f'{now_as_str()}.csv'
ZALANDO_FEED_URL = (
    f'https://merchants-connector-importer.zalandoapis.com/{ZALANDO_CLIENT_ID}/{FEED_NAME}')

if not all([ZALANDO_CLIENT_ID, ZALANDO_API_KEY, ZALANDO_FEED_PATH]):
    print("\ncheck you environment variables - do you what you are doing son?\n")
    sys.exit(1)


HEADER = [
    'store', 'ean', 'price', 'retail_price', 'quantity', 'article_number',
    'article_color', 'product_name', 'store_article_location', 'product_number',
    'article_size']

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


# FACTOR = 1.2
FACTOR = get_z_factor()
SHIPPING_FEE = 3.95


def _get_price(price):
    """Return beautiful price after factor was applied."""
    price = round(price * FACTOR, 2) + SHIPPING_FEE

    while True:
        # print(price)
        price = round(price + 0.01, 2)
        if price in PRICES:
            return price

        if price > 200:
            # This should never happen
            return 'ERROR'


class Command(BaseCommand):
    help = "Update product feed at zalando"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry', type=int,
            nargs='?',  # argument is optional
            help='When dry run, the final feedupload is not done (only validation)',
            default=0)

    def handle(self, *args, **kwargs):
        """Download product feed from shop and transmit it to Z for validation"""
        dry_run = kwargs.get('dry')
        response = requests.get(ZALANDO_FEED_PATH)
        decoded_content = response.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=';')
        csv_content_as_list = list(cr)

        print(f'Houston we have a csv with {len(csv_content_as_list)} lines')

        lines = []
        ignores = {'no_ean': 0, 'no_quantity': 0}

        path_origin_feed = os.path.join(
            settings.MEDIA_ROOT, 'original', f'{now_as_str()}.csv')

        with open(path_origin_feed, 'w', encoding='UTF8') as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            for idx, row in enumerate(csv_content_as_list):
                #
                # ROW is [
                #   'store', 'ean', 'price', 'retail_price', 'quantity',
                #   'article_number', 'article_color', 'product_name',
                #   'store_article_location', 'product_number', 'article_size']
                # import ipdb; ipdb.set_trace()
                #
                if row[1] == '':
                    # print(f'SKIP LINE No {idx} - no ean - {row[5]} - {row[7]}')
                    ignores['no_ean'] += 1
                    continue

                if row[4] == '':
                    print(f'LINE No {idx} - no quantity - {row[7]}')
                    ignores['no_quantity'] += 1
                    row[4] = 0

                writer.writerow(row)
                lines.append(row)

        number_of_valid_items = len(lines)
        LOG.info(f'Houston we have a csv with {len(lines)} lines')
        LOG.info(f'Ignores: {ignores}')

        headers = {
            'x-api-key': ZALANDO_API_KEY,
            'content-type': "application/csv",
            'cache-control': "no-cache"
        }

        with open(path_origin_feed, 'rb') as f:
            resp = requests.put(
                ZALANDO_VALIDATION_URL,
                headers=headers,
                data=f.read())

        LOG.info(f'Response code: {resp.status_code}')
        status_code_validation = resp.status_code

        for row in lines[1:]:
            # print(row)
            # 2 price
            # 3 retail_price
            # 7 name
            ean = row[1]
            original_price = float(row[2])
            price = _get_price(float(row[2]))
            retail_price = _get_price(float(row[3]))
            product_name = row[7]
            LOG.debug(f'{product_name}: {original_price} -> {price}')
            Product.objects.get_or_create(ean=ean, defaults={
                'title': product_name
            })

            row[2] = str(price)
            row[3] = str(retail_price)

        pimped_file_name = os.path.join(
            settings.MEDIA_ROOT, 'pimped', f'{now_as_str()}.csv')
        with open(pimped_file_name, 'w', encoding='UTF8') as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            for row in lines:
                writer.writerow(row)

        with open(pimped_file_name, 'rb') as f:
            resp = requests.put(
                ZALANDO_VALIDATION_URL,
                headers=headers,
                data=f.read())

        LOG.info(f'Response code (validation): {resp.status_code}')
        LOG.info(resp.json())

        if dry_run:
            LOG.info('Return early because of --dry-run')
            return
        else:
            LOG.info('Uploading transformed feed now')

        with open(pimped_file_name, 'rb') as f:
            resp = requests.put(
                ZALANDO_FEED_URL,
                headers=headers,
                data=f.read())

        # Response is empty - b''
        LOG.info(f'Response code (feed): {resp.status_code}')
        status_code_feed_upload = resp.status_code

        fupload = FeedUpload(
            status_code_validation=status_code_validation,
            status_code_feed_upload=status_code_feed_upload,
            number_of_valid_items=number_of_valid_items,
            path_to_original_csv=path_origin_feed,
            path_to_pimped_csv=pimped_file_name,
            z_factor=FACTOR
        )
        fupload.save()
