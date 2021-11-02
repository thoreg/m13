"""Esty views.

OAuth Information:
https://developers.etsy.com/documentation/essentials/authentication/#proof-key-for-code-exchange-pkce

"""
import logging
import os
from pprint import pformat

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from m13.common import base64_encode

from .models import AuthGrant, AuthToken
from .services import get_receipts, process_receipts

LOG = logging.getLogger(__name__)

M13_ETSY_API_KEY = os.getenv('M13_ETSY_API_KEY')
M13_ETSY_GET_AUTH_TOKEN_URL = 'https://api.etsy.com/v3/public/oauth/token'
M13_ETSY_OAUTH_REDIRECT = os.getenv('M13_ETSY_OAUTH_REDIRECT')
M13_ETSY_SHOP_ID = os.getenv('M13_ETSY_SHOP_ID')


def _render_auth_request_not_found(request):
    ctx = {
        'error': 'AuthRequest2.DoesNotExist',
        'error_descrption': 'No AuthRequest2 found'
    }
    return render(request, 'etsy/oauth_error.html', ctx)


def orders(request):
    """Display orders from etsy."""
    try:
        auth_token = AuthToken.objects.all().order_by('-created')[0]
        response = get_receipts(auth_token.token)
        process_receipts(response)

    except IndexError:
        _render_auth_request_not_found(request)

    ctx = {
        'response': 'coming_soon'
    }
    return render(request, 'etsy/orders.html', ctx)


def refresh(request):
    """Refresh Auth Token."""
    try:
        auth_request = AuthToken.objects.all().order_by('-created')[0]
        refresh_token = auth_request.refresh_token
    except IndexError:
        _render_auth_request_not_found(request)

    req_body = {
        'client_id': M13_ETSY_API_KEY,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }

    LOG.info(f'POST: req_body {req_body}')
    resp = requests.post(M13_ETSY_GET_AUTH_TOKEN_URL, data=req_body)

    resp_json = resp.json()
    LOG.info('- POST RESPONSE REFRESH ------------------------------------')
    LOG.info(resp_json)
    LOG.info('- POST RESPONSE REFRESH -------------------------------- END')

    AuthToken.objects.create(
        token=resp_json.get('access_token'),
        refresh_token=resp_json.get('refresh_token')
    )


def oauth(request):
    """OAuth redirect url."""
    error = request.GET.get('error')
    if error:
        error_description = request.GET.get('error_description')
        ctx = {
            'error': error,
            'error_descrption': error_description
        }
        return render(request, 'etsy/oauth_error.html', ctx)
    else:
        auth_code = request.GET.get('code')
        state = request.GET.get('state')
        try:
            auth_request = AuthGrant.objects.get(
                state=state,
            )
        except AuthGrant.DoesNotExist:
            _render_auth_request_not_found(request)

        # Verify functionality - qqq
        req_body = {
            'client_id': M13_ETSY_API_KEY,
            'code_verifier': auth_request.verifier.encode('utf8'),
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': M13_ETSY_OAUTH_REDIRECT,
        }
        LOG.info(f'POST: req_body {req_body}')
        resp = requests.post(M13_ETSY_GET_AUTH_TOKEN_URL, data=req_body)
        resp_json = resp.json()
        LOG.info('- POST RESPONSE ---------------------------------------')
        LOG.info(resp_json)
        LOG.info('- POST RESPONSE ----------------------------------- END')

        AuthToken.objects.create(
            token=resp_json.get('access_token'),
            refresh_token=resp_json.get('refresh_token')
        )

        context = {
            'msg': 'Hooray we have an AUTH_TOKEN'
        }
        return render(request, 'etsy/oauth_success.html', context)


@login_required
def index(request):
    """Index view of the etsy app."""
    token = None
    refresh_token = None
    try:
        auth_request = AuthToken.objects.all().order_by('-created')[0]
        token = auth_request.auth_token
        refresh_token = auth_request.refresh_token
    except IndexError:
        pass

    ctx = {
        'token': token,
        'refresh_token': refresh_token
    }

    return render(request, 'etsy/index.html', ctx)
