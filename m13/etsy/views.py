import base64
import hashlib
import logging
import os
import secrets
from pprint import pformat

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

LOG = logging.getLogger(__name__)


def oauth(request):
    """OAuth redirect url."""
    LOG.info('oauth redirect route called')
    LOG.info(pformat(request.__dict__))

    context = {}
    return render(request, 'etsy/oauth.html', context)


@login_required
def index(request):

    LOG.info(pformat(request.__dict__))

    # // The next two functions help us generate the code challenge
    # // required by Etsy’s OAuth implementation.
    # const base64URLEncode = (str) =>
    #   str
    #     .toString("base64")
    #     .replace(/\+/g, "-")
    #     .replace(/\//g, "_")
    #     .replace(/=/g, "");

    # const sha256 = (buffer) => crypto.createHash("sha256").update(buffer).digest();

    # // We’ll use the verifier to generate the challenge.
    # // The verifier needs to be saved for a future step in the OAuth flow.
    # const codeVerifier = base64URLEncode(crypto.randomBytes(32));

    # // With these functions, we can generate
    # // the values needed for our OAuth authorization grant.
    # const codeChallenge = base64URLEncode(sha256(codeVerifier));
    # const state = Math.random().toString(36).substring(7);

    def _encode(blo):
        """Return encoded byte like object."""
        return base64.urlsafe_b64encode(blo)

    verifier = _encode(secrets.token_hex(32).encode('utf-8'))
    print(f'verifier: {verifier}')

    code_challenge = _encode(
        (hashlib.sha256(verifier).hexdigest()).encode('utf-8'))
    print(f'code_challenge: {code_challenge}')

    context = {
        'api_key': os.getenv('M13_ETSY_KEY'),
        'code_challenge': code_challenge,
        'redirect_uri': 'https://m13.thoreg.com/etsy/oauth',
        'scope': 'transactions_r%20listings_r',
        'superstring': 'supergirLZd0ntCRY2013!',
        'verifier': verifier,
    }
    return render(request, 'etsy/index.html', context)
