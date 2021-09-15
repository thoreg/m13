import logging
import os
import sys
from functools import reduce

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

LOG = logging.getLogger(__name__)

M13_URL = 'https://www.manufaktur13.de/shop/'
LOGO_URL = 'https://www.manufaktur13.de/wp-content/uploads/2017/08/navicon.png'

ALLOWED_STARTER = [
    '?add_to_wishlist',
    '?add-to-cart',
]

M13_SHOP = 'https://www.manufaktur13.de'

WHITE_LIST = [
    None,
    '#',
    '#0',
    'https://www.youtube.com/c/Manufaktur13De/videos',
    'https://www.facebook.com/pages/Manufaktur-13/510954562300442',
    'https://www.pinterest.de/manufaktur130311/',
    'https://www.instagram.com/manufaktur13/',
    'https://www.youtube.com/channel/UCLHKAq7rTPTOcPTGXygkeLg',
    'javascript:void(0);',
]


class Command(BaseCommand):
    help = "Check if the shop is up and running."

    def suspicious(self, msg):
        LOG.error(f'SNEAKY PETE detected - suspicious: "{msg}"')
        sys.exit(-1)

    def handle(self, *args, **kwargs):
        """..."""
        resp = requests.get(M13_URL)
        if resp.status_code != requests.codes.ok:
            LOG.error('Status is NOT 200')
            sys.exit(-1)

        soup = BeautifulSoup(resp.text, 'html.parser')

        logo = soup.findAll('img', {'class': 'site-logo'})
        # One normal + one lazy load
        if len(logo) != 2:
            return self.suspicious('Logo not found')

        if logo[0]['src'] != LOGO_URL:
            return self.suspicious('Logo has not the right URL')

        for link in soup.find_all('a'):
            print(link.get('href'))
            href = link.get('href')

            if href in WHITE_LIST:
                continue

            elif href.startswith(M13_SHOP):
                continue

            else:
                suspicious = True
                for allowed in ALLOWED_STARTER:
                    if href.startswith(allowed):
                        suspicious = False
                        break

                if suspicious:
                    return self.suspicious(f'strange href: {href}')

        LOG.info('All fine')
        sys.exit(0)
