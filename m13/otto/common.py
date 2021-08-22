"""Common stuff used all over the code."""

import os
import sys

import requests

TOKEN_URL = "https://api.otto.market/v1/token"

USERNAME = os.getenv("OTTO_API_USERNAME")
PASSWORD = os.getenv("OTTO_API_PASSWORD")


if not all([USERNAME, PASSWORD]):
    print("\nyou need to define username and password\n")
    sys.exit(1)


def get_auth_token():
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
    )
    return r.json().get("access_token")


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict.

    Stolen from https://docs.djangoproject.com/en/dev/topics/db/sql/
    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
