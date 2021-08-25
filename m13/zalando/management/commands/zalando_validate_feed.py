import os
import io
import sys
import csv
from pprint import pprint
from django.core.management.base import BaseCommand

import requests

ZALANDO_FEED_PATH = os.getenv('ZALANDO_M13_FEED')
ZALANDO_API_KEY = os.getenv('ZALANDO_API_KEY')
ZALANDO_CLIENT_ID = os.getenv('ZALANDO_CLIENT_ID')
ZALANDO_VALIDATION_URL = (
    f'https://merchants-connector-importer.zalandoapis.com/{ZALANDO_CLIENT_ID}/validate')

if not all([ZALANDO_CLIENT_ID, ZALANDO_API_KEY, ZALANDO_FEED_PATH]):
    print("\ncheck you environment variables - do you what you are doing son?\n")
    sys.exit(1)


HEADER = [
    'store', 'ean', 'price', 'retail_price', 'quantity', 'article_number',
    'article_color', 'product_name', 'store_article_location', 'product_number',
    'article_size']


class Command(BaseCommand):
    help = "Update product feed at zalando"

    def handle(self, *args, **kwargs):
        """Download product feed from shop and transmit it to Z for validation"""

        all_rows = {}

        # begin - get feed from M13

        response = requests.get(ZALANDO_FEED_PATH)
        decoded_content = response.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=';')
        csv_content_as_list = list(cr)

        print(f'Houston we have a csv with {len(csv_content_as_list)} lines')
        # for row in csv_content_as_list:
        #     print(row)

        with open('z.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            for idx, row in enumerate(csv_content_as_list):
                writer.writerow(row)

                idx += 1  # line count in error/warning reporting starts with 1
                all_rows[idx] = {}
                all_rows[idx]['row'] = row
                all_rows[idx]['warnings'] = []

        # end - get feed from M13

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
        # import ipdb; ipdb.set_trace()

        warnings = resp.json()['warnings']
        for warning in warnings:
            # pprint(warning)
            for line_number in warning['line_numbers']:
                try:
                    all_rows[line_number]['warnings'].append(
                        (warning['type'], warning['message'])
                    )
                except KeyError:
                    import ipdb; ipdb.set_trace()

        print('LADIES AND GENTLEMEN - ROWS WITHOUT WARNINGS: ')
        valid_rows = []
        for line_number, data in all_rows.items():
            if len(data.get('warnings')):
                continue
            # print(f'{line_number} {data.get("row")}')
            valid_rows.append(data.get("row"))

        print(f'number of valid rows: {len(valid_rows)}')

        with open('valid_z.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            for row in valid_rows:
                writer.writerow(row)

        with open('valid_z.csv', 'rb') as f:
            resp = requests.put(
                ZALANDO_VALIDATION_URL,
                headers=headers,
                data=f.read())

        print(f'Response code: {resp.status_code}')
        print(resp.json())
