import logging
import os

import requests

from etsy.models import AuthToken

LOG = logging.getLogger(__name__)

M13_ETSY_API_KEY = os.getenv('M13_ETSY_API_KEY')
M13_ETSY_SHOP_ID = os.getenv('M13_ETSY_SHOP_ID')

M13_ETSY_GET_AUTH_TOKEN_URL = 'https://api.etsy.com/v3/public/oauth/token'


def get_auth_token():
    """Return new shiny and fresh auth token."""
    try:
        auth_token = AuthToken.objects.all().order_by('-created')
        if not auth_token:
            raise AuthToken.DoesNotExist()
        refresh_token = auth_token[0].refresh_token
    except AuthToken.DoesNotExist:
        LOG.error('No auth token found')
        return None

    req_body = {
        'client_id': M13_ETSY_API_KEY,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }

    LOG.info(f'POST: req_body {req_body}')
    resp = requests.post(M13_ETSY_GET_AUTH_TOKEN_URL, data=req_body)
    resp_json = resp.json()
    LOG.info(resp_json)

    AuthToken.objects.create(
        token=resp_json.get('access_token'),
        refresh_token=resp_json.get('refresh_token')
    )

    return resp_json.get('access_token')
