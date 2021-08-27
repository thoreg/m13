import csv
import io
import os
import sys
from datetime import datetime
from pprint import pprint

import requests
from django.core.management.base import BaseCommand

ZALANDO_FEED_PATH = os.getenv('ZALANDO_M13_FEED')
ZALANDO_API_KEY = os.getenv('ZALANDO_API_KEY')
ZALANDO_CLIENT_ID = os.getenv('ZALANDO_CLIENT_ID')
ZALANDO_VALIDATION_URL = (
    f'https://merchants-connector-importer.zalandoapis.com/{ZALANDO_CLIENT_ID}/validate')

now = datetime.now()
now_as_str = now.strftime('%Y-%m-%dT%H%M%S')
FEED_NAME = f'{now_as_str}.csv'
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

FACTOR = 1.2
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

    def handle(self, *args, **kwargs):
        """Download product feed from shop and transmit it to Z for validation"""
        response = requests.get(ZALANDO_FEED_PATH)
        decoded_content = response.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=';')
        csv_content_as_list = list(cr)

        print(f'Houston we have a csv with {len(csv_content_as_list)} lines')

        lines = []
        ignores = {'no_ean': 0, 'no_quantity': 0}
        with open('z.csv', 'w', encoding='UTF8') as f:
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
                    print(f'SKIP LINE No {idx} - no ean - {row[7]}')
                    ignores['no_ean'] += 1
                    continue

                if row[4] == '':
                    print(f'LINE No {idx} - no quantity - {row[7]}')
                    ignores['no_quantity'] += 1
                    row[4] = 0

                writer.writerow(row)
                lines.append(row)

        print(f'Houston we have a csv with {len(lines)} lines')
        print(f'Ignores: {ignores}')

        headers = {
            'x-api-key': ZALANDO_API_KEY,
            'content-type': "application/csv",
            'cache-control': "no-cache"
        }

        with open('z.csv', 'rb') as f:
            resp = requests.put(
                ZALANDO_VALIDATION_URL,
                headers=headers,
                data=f.read())

        print(f'Response code: {resp.status_code}')
        # print(resp.json())

        for row in lines[1:]:
            # print(row)
            # 2 price
            # 3 retail_price
            # 7 name
            original_price = float(row[2])
            price = _get_price(float(row[2]))
            retail_price = _get_price(float(row[3]))
            product_name = row[7]
            print(f'{product_name}: {original_price} -> {price}')

            row[2] = str(price)
            row[3] = str(retail_price)

        pimped_file_name = 'valid_z_pimped_20_percent.csv'
        with open(pimped_file_name, 'w', encoding='UTF8') as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            for row in lines:
                writer.writerow(row)

        with open(pimped_file_name, 'rb') as f:
            resp = requests.put(
                ZALANDO_VALIDATION_URL,
                headers=headers,
                data=f.read())

        print(f'Response code (validation): {resp.status_code}')
        print(resp.json())

        with open(pimped_file_name, 'rb') as f:
            resp = requests.put(
                ZALANDO_FEED_URL,
                headers=headers,
                data=f.read())

        print(f'Response code (feed): {resp.status_code}')
        print(resp.json())
