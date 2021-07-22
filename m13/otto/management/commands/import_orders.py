import os
import sys
from fastapi import FastAPI
import requests
import json
from requests.auth import HTTPBasicAuth
from django.core.management.base import BaseCommand, CommandError


TOKEN_URL = "https://api.otto.market/v1/token"
ORDERS_URL = "https://api.otto.market/v4/orders"

USERNAME = os.getenv("OTTO_API_USERNAME")
PASSWORD = os.getenv("OTTO_API_PASSWORD")

token = ""

if not all([USERNAME, PASSWORD]):
    print("\nyou need to define username and password\n")
    sys.exit(1)


class Command(BaseCommand):
    help = "Import Orders from OTTO"

    def handle(self, *args, **options):

        print(f"Get the token ...")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache",
        }
        data = {
            "username": USERNAME,
            "grant_type": "password",
            "client_id": "token-otto-api",
            "password": PASSWORD,
        }
        r = requests.post(
            TOKEN_URL,
            headers=headers,
            data=data,
        )
        response = r.json()
        token = response.get("access_token")

        print(f"Get the orders ...")
        headers = {
            "Authorization": f"Bearer {token}",
        }
        r = requests.get(
            ORDERS_URL,
            headers=headers,
        )
        print(f"response_status_code: {r.status_code}")
        response = r.json()
        print(response)

        for order in response.get("resources", []):
            import ipdb

            ipdb.set_trace()

        self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % 999))
