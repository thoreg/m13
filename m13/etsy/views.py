"""Esty views.

OAuth Information:
https://developers.etsy.com/documentation/essentials/authentication/#proof-key-for-code-exchange-pkce

"""
import base64
import hashlib
import logging
import os
import random
import secrets
import string
from pprint import pformat

import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render

from m13.common import base64_encode

from .models import AuthRequest2

LOG = logging.getLogger(__name__)

M13_ETSY_API_KEY = os.getenv('M13_ETSY_API_KEY')
M13_ETSY_GET_AUTH_TOKEN_URL = 'https://api.etsy.com/v3/public/oauth/token'
M13_ETSY_OAUTH_REDIRECT = os.getenv('M13_ETSY_OAUTH_REDIRECT')


def orders(request):
    """Display orders from etsy."""
    token = 'NOT_SET_YET'
    try:
        auth_request = AuthRequest2.objects.all().order_by('-created')[0]
        token = auth_request.auth_token
    except IndexError:
        pass

    ctx = {
        'token': token
    }
    return render(request, 'etsy/orders.html', ctx)


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
            auth_request = AuthRequest2.objects.get(
                state=state,
            )
        except AuthRequest2.DoesNotExist:
            ctx = {
                'error': 'AuthRequest2.DoesNotExist',
                'error_descrption': 'AuthRequest2.DoesNotExist'
            }
            return render(request, 'etsy/oauth_error.html', ctx)

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

        auth_request.auth_token = resp_json['access_token']
        auth_request.refresh_token = resp_json['refresh_token']
        auth_request.save()

        context = {
            'msg': 'Hooray we have an AUTH_TOKEN',
            'token': auth_request.auth_token
        }
        return render(request, 'etsy/oauth_success.html', context)


@login_required
def index(request):
    """Index view of the etsy app.

    Responsible to genere everything needed for auth token request.
    """
    # sanity checks
    if not M13_ETSY_API_KEY:
        msg = 'M13_ETSY_API_KEY needed - do you know what you are doing?'
        return HttpResponseNotFound(f'<h1>{msg}</h1>')

    if not M13_ETSY_OAUTH_REDIRECT:
        msg = 'M13_ETSY_OAUTH_REDIRECT needed - do you know what you are doing?'
        return HttpResponseNotFound(f'<h1>{msg}</h1>')

    # We’ll use the verifier to generate the challenge.
    # The verifier needs to be saved for a future step in the OAuth flow.
    verifier = base64_encode(secrets.token_hex(32).encode('utf8'))
    LOG.info(f'[ index ] verifier: {verifier}')

    # the PKCE (Proof Key for Code Exchange) code challenge generated from
    # the code verifier above
    code_challenge = base64_encode(
        (hashlib.sha256(verifier).hexdigest()).encode('utf-8'))
    LOG.info(f'[ index ] code_challenge: {code_challenge}')

    # A string which Etsy.com should return with the authorization code
    MAX_STATE_LENGTH = 8
    state = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(MAX_STATE_LENGTH))
    LOG.info(f'[ index ] state: {state}')

    # Scope: we want listings and transactions (orders)
    scope = 'transactions_r%20listings_r%20email_r'
    LOG.info(f'[ index ] scope: {scope}')

    AuthRequest2.objects.create(
        verifier=verifier.decode('utf8'),
        code_challenge=code_challenge.decode('utf8'),
        state=state,
    )

    context = {
        'api_key': M13_ETSY_API_KEY,
        'code_challenge': code_challenge,
        'redirect_uri': M13_ETSY_OAUTH_REDIRECT,
        'scope': scope,
        'state': state,
        'verifier': verifier,
    }
    return render(request, 'etsy/index.html', context)
