"""Common stuff used all over the code."""

import os
import sys
from pprint import pprint

import requests

TOKEN_URL = "https://api.otto.market/v1/token"

CLIENT_ID = os.getenv("OTTO_API_CLIENT_ID")
CLIENT_SECRET = os.getenv("OTTO_API_CLIENT_SECRET")


if not all([CLIENT_ID, CLIENT_SECRET]):
    print("\nyou need to define client_id and client_secret\n")
    sys.exit(1)


def get_auth_token():
    """Get authentication token for further communication."""
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache",
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "orders products shipments availability",
    }
    r = requests.post(
        TOKEN_URL,
        headers=headers,
        data=data,
        timeout=60,
    )

    pprint(r.json())
    return r.json().get("access_token")
