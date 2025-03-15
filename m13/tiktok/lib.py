import csv
import logging
import os

import requests

from m13.lib import log as mlog

from .models import AuthToken

LOG = logging.getLogger(__name__)

M13_TIKTOK_APP_KEY = os.getenv("M13_TIKTOK_APP_KEY")
M13_TIKTOK_APP_SECRET = os.getenv("M13_TIKTOK_APP_SECRET")

M13_TIKTOK_AUTH_TOKEN_URL = "https://auth.tiktok-shops.com/api/v2/token/get"
M13_TIKTOK_REFRESH_TOKEN_URL = "https://auth.tiktok-shops.com/api/v2/token/refresh"


def get_access_token():
    """Get and refresh the access token."""
    url = M13_TIKTOK_REFRESH_TOKEN_URL
    try:
        auth_token = AuthToken.objects.all().order_by("-created")
        if not auth_token:
            raise AuthToken.DoesNotExist()

    except AuthToken.DoesNotExist:
        mlog.error(LOG, "No auth token found")
        return None

    payload = {
        "app_key": M13_TIKTOK_APP_KEY,
        "app_secret": M13_TIKTOK_APP_SECRET,
        "refresh_token": auth_token[0].refresh_token,
        "grant_type": "refresh_token",
    }
    resp = requests.get(url, params=payload)

    if resp.status_code != requests.codes.ok:
        LOG.error(resp)
        return

    resp_json = resp.json()
    access_token = resp_json["data"]["access_token"]
    refresh_token = resp_json["data"]["refresh_token"]

    AuthToken.objects.create(token=access_token, refresh_token=refresh_token)

    return access_token


def download_feed(download_url: str):
    """Download feed from M13 shop and return list of stock."""
    response = requests.get(download_url)
    LOG.info(f"Download from {download_url} - status: {response.status_code}")
    decoded_content = response.content.decode("utf-8")
    cr = csv.DictReader(decoded_content.splitlines(), delimiter=";")
    return list(cr)
