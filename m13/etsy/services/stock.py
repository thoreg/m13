import json
import logging
import os
from pprint import pprint

import django
import requests
from requests.models import codes

from etsy.common import get_auth_token
from etsy.models import Listing
from m13.lib.zfeed import download_feed, filter_feed

M13_ETSY_API_KEY = os.getenv("M13_ETSY_API_KEY")
M13_ETSY_SHOP_ID = os.getenv("M13_ETSY_SHOP_ID")

LIMIT = 64
MAX_QUANTITY = 999

LOG = logging.getLogger(__name__)


class EtsyNoTokenDiggiException(Exception):
    """..."""

    ...


class RequestFailed(Exception):
    """..."""

    ...


class EtsyStockSync:

    def __init__(self):
        self.token = get_auth_token()
        if not self.token:
            raise EtsyNoTokenDiggiException("No auth token found")

        self.headers = {
            "x-api-key": M13_ETSY_API_KEY,
            "authorization": f"Bearer {self.token}",
        }

        user_info_url = "https://openapi.etsy.com/v3/application/users/me"
        r = requests.get(user_info_url, headers=self.headers)
        r_json = r.json()

        self.shop_id = r_json["shop_id"]

    def sync_active_listings(self):
        """Download info about active listings."""
        LOG.info("sync_active_listings() starting ...")

        _offset = 0
        count = self._get_active_listings()
        while _offset < count:
            _offset += LIMIT
            self._get_active_listings(offset=_offset)

        self._get_active_listings(offset=_offset)

    def _get_active_listings(self, offset: int = 0, limit: int = LIMIT) -> int:
        base_url = f"https://openapi.etsy.com/v3/application/shops/{self.shop_id}/listings/active"
        url = f"{base_url}?offset={offset}&limit={limit}"
        r = requests.get(url, headers=self.headers)

        if r.status_code != codes.ok:
            LOG.error(f"Request failed with status code {r.status_code}")
            LOG.error(r.json())
            raise RequestFailed()

        resp_json = r.json()
        count = resp_json["count"]
        results = resp_json["results"]

        self.__update_listings(results)

        return count

    def __update_listings(self, entries: list):
        for entry in entries:
            # import ipdb ; ipdb.set_trace()
            listing_id = entry["listing_id"]
            sku = entry["skus"]

            # das geraet hier alles ausser kontrolle -> mach ne Klasse draus
            GET_PROPERTIES_URL = f"https://openapi.etsy.com/v3/application/shops/{self.shop_id}/listings/{listing_id}/properties"
            response = requests.get(GET_PROPERTIES_URL, headers=self.headers)

            if response.status_code != codes.ok:
                LOG.error(f"Request failed with status code {response.status_code}")
                LOG.error(response.json())
                raise RequestFailed()

            if len(sku) > 1:
                LOG.error("---")
                LOG.error(f"More than one sku found for {listing_id}")
                LOG.error(f"skus: {sku}")
                LOG.error(f"quantity: {entry['quantity']}")
                continue

            if len(sku) == 0:
                LOG.error("---")
                LOG.error(f"No sku found for {listing_id}")
                LOG.error(f"entry: {entry}")
                continue

            resp_json = response.json()
            sku = entry["skus"][0]
            try:
                created, _obj = Listing.objects.get_or_create(
                    listing_id=listing_id,
                    defaults={
                        "sku": sku,
                        "price_in_cent": entry["price"]["amount"],
                        "quantity": entry["quantity"],
                        "property_id": resp_json["results"][0]["property_id"],
                    },
                )
                if created:
                    LOG.info(f"{listing_id} : {sku} : created")
                else:
                    LOG.info(f"{listing_id} : {sku} : already known")

            except django.db.utils.IntegrityError:
                LOG.error("---")
                LOG.exception(f"{listing_id} : {sku} Integrity Error")
                continue

    def sync_stock(self):
        """Upload stock information to etsy."""
        LOG.info("sync_stock() starting ...")

        # Setup data
        original_feed = download_feed()
        sku_quantity_price_map = filter_feed(original_feed)
        LOG.info(f"len(sku_quantity_price_map): {len(sku_quantity_price_map)}")
        data = {
            "items": [
                {"sku": sku, "quantity": quantity}
                for sku, quantity, _price in sku_quantity_price_map
            ]
        }
        skus_from_zfeed = [e["sku"] for e in data["items"]]

        data_from_zfeed = {
            f"{sku}": quantity for sku, quantity, _price in sku_quantity_price_map
        }

        # TEST_SKUS = [
        #     "WBG2-BO",
        #     "WBG2-HE",
        #     "KB007",
        #     "CBBDuffle-OL",
        #     "KLOOP-MU",
        # ]

        updates_with_issues = {}

        # for sku in TEST_SKUS:
        for sku in skus_from_zfeed:
            if sku not in data_from_zfeed:
                LOG.warning(f"{sku} not in zfeed")
                continue

            try:
                listing = Listing.objects.get(sku=sku)
            except Listing.DoesNotExist:
                LOG.warning(f"{sku} not found in etsy listings")
                continue

            listing_id = listing.listing_id
            INVENTORY_URL = f"https://openapi.etsy.com/v3/application/listings/{listing_id}/inventory"
            r = requests.get(INVENTORY_URL, headers=self.headers)

            if r.status_code != codes.ok:
                LOG.error(f"Request failed with status code {r.status_code}")
                LOG.error(r.json())
                continue

            inventory_data = r.json()

            quantity_m13 = int(data_from_zfeed[f"{sku}"])
            if quantity_m13 > MAX_QUANTITY:
                quantity_m13 = MAX_QUANTITY
            quantity_etsy = inventory_data["products"][0]["offerings"][0]["quantity"]
            LOG.info(f"inventory: {sku} - m13: {quantity_m13} VS etsy: {quantity_etsy}")

            if int(quantity_m13) == int(quantity_etsy):
                LOG.info(f"quantity for sku: {sku} is in sync : {quantity_etsy}")
                continue

            # Cleanup fields which are not part of the payload for the PUT call
            # https://github.com/etsy/open-api/discussions/1176
            del inventory_data["products"][0]["offerings"][0]["is_deleted"]
            del inventory_data["products"][0]["offerings"][0]["offering_id"]
            del inventory_data["products"][0]["product_id"]
            del inventory_data["products"][0]["is_deleted"]

            offering = inventory_data["products"][0]["offerings"][0]
            price = offering["price"]["amount"] / offering["price"]["divisor"]

            inventory_data["products"][0]["offerings"][0]["price"] = price
            inventory_data["products"][0]["offerings"][0]["quantity"] = quantity_m13

            resp = requests.put(
                INVENTORY_URL, headers=self.headers, json=inventory_data
            )

            if resp.status_code != codes.ok:
                resp_json = resp.json()
                LOG.error(f"Request failed with status code {resp.status_code}")
                LOG.error(resp_json)

                # {
                #     'resp_json': {'error': 'One offering must have quantity greater than 0'},
                #     'sku': 'SM008',
                #     'status_code': 400
                # }
                if resp_json["error"] == "One offering must have quantity greater than 0":
                    inventory_data["products"][0]["offerings"][0]["is_enabled"] = False
                    inventory_data["products"][0]["offerings"][0]["quantity"] = 1

                    resp = requests.put(
                        INVENTORY_URL, headers=self.headers, json=inventory_data
                    )

                    if resp.status_code != codes.ok:
                        resp_json = resp.json()
                        LOG.error(f"Request failed with status code {resp.status_code}")
                        LOG.error(resp_json)
                        updates_with_issues[sku] = {
                           "sku": sku,
                            "status_code": resp.status_code,
                            "resp_json": resp_json,
                        }

                else:
                    updates_with_issues[sku] = {
                        "sku": sku,
                        "status_code": resp.status_code,
                        "resp_json": resp_json,
                    }

        LOG.warning("sync stock updates with issues: ")
        for entry in updates_with_issues:
            # pprint(updates_with_issues[entry])
            LOG.warning(updates_with_issues[entry])
