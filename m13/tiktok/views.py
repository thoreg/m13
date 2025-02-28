import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

LOG = logging.getLogger(__name__)

LOCATION = "tiktok"


@login_required
def index(request) -> HttpResponse:
    """..."""
    context = {
        "location": LOCATION,
    }
    return render(request, "tiktok/index.html", context)


def authcode(request) -> HttpResponse:
    """..."""
    for k, v in request.GET.items():
        LOG.info(f"{k}: {v}")
    context = {
        "location": LOCATION,
    }
    return render(request, "tiktok/index.html", context)
