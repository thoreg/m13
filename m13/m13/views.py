from datetime import datetime, timedelta, timezone

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from zalando.models import FeedUpload


def page_not_found_view(request, exception):
    return render(request, "404.html", status=404)


@login_required
def index(request):
    now = datetime.now(timezone.utc)
    feed_upload = FeedUpload.objects.latest("created")

    delta = now - feed_upload.created

    if delta > timedelta(hours=1):
        messages.error(request, f"Last feed upload to Z {delta} ago")
    else:
        messages.success(request, f"Last feed upload to Z {delta} ago")

    return render(request, "m13/index.html", {})
