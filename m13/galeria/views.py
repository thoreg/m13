import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import FeedUpload

LOG = logging.getLogger(__name__)
LOCATION = "galeria"


@login_required
def index(request):
    """Galeria Index View."""
    return render(request, "galeria/index.html", {"location": LOCATION})


@login_required
def price_feed(request):
    """Price Feed Index View for Galeria."""
    feed_uploads = FeedUpload.objects.all().order_by("-created")[:5]
    ctx = {
        "feed_uploads": feed_uploads,
        "location": LOCATION,
    }
    return render(request, "galeria/price_feed.html", ctx)
