"""Simple starter to poke around in the Galeria API."""

import logging
import os
from pprint import pprint
import requests

from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand


LOG = logging.getLogger(__name__)

OFFERS_URL = "https://galeria.mirakl.net/api/offers"

class Command(BaseCommand):
    """..."""

    help = "__doc__"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry",
            type=int,
            nargs="?",  # argument is optional
            help="When dry run, the final feedupload is not done (only validation)",
            default=0,
        )

    def __print_offers(self, entries: list[dict]):
        for idx, entry in enumerate(entries):
            print(f"[{idx:02}] {entry['shop_sku']} {entry['total_price']} {entry['quantity']}")
            pprint(entry)
            import ipdb ; ipdb.set_trace()

    def handle(self, *args, **kwargs):
        """Download product feed from shop and transmit it to Z for validation"""
        M13_GALERIA_API_KEY = os.getenv("M13_GALERIA_API_KEY")
        if not M13_GALERIA_API_KEY:
            LOG.error("M13_GALERIA_API_KEY is empty")
            return

        headers = {
            "Authorization": M13_GALERIA_API_KEY
        }

        offset = 0
        url = f"{OFFERS_URL}?max=100&offset={offset}"
        response = requests.get(url, headers=headers)
        self.__print_offers(response.json()["offers"])

        while response.links.get("next"):
            url = response.links["next"]["url"]
            response = requests.get(url, headers=headers)
            self.__print_offers(response.json()["offers"])
            print("\n\n")
