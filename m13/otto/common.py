"""Common stuff used all over the code."""

import os
import sys
from pprint import pprint

import requests

TOKEN_URL = "https://api.otto.market/v1/token"

USERNAME = os.getenv("OTTO_API_USERNAME")
PASSWORD = os.getenv("OTTO_API_PASSWORD")

CLIENT_ID = os.getenv("OTTO_API_CLIENT_ID")
CLIENT_SECRET = os.getenv("OTTO_API_CLIENT_SECRET")


if not all([USERNAME, PASSWORD]):
    print("\nyou need to define username and password\n")
    sys.exit(1)

if not all([CLIENT_ID, CLIENT_SECRET]):
    print("\nyou need to define client_id and client_secret\n")
    sys.exit(1)


def __old__get_auth_token():
    """Get authentication token for further communication."""
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
        timeout=60,
    )

    pprint(r.json())
    return r.json().get("access_token")


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
        "scope": "orders products",
    }
    r = requests.post(
        TOKEN_URL,
        headers=headers,
        data=data,
        timeout=60,
    )

    pprint(r.json())
    return r.json().get("access_token")
