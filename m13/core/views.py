import logging
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .services.article_stats import get_article_stats

LOG = logging.getLogger(__name__)


@login_required
def return_shipments_stats(request):
    """Overview of all zalando calculator values."""
    return render(request, "core/return_shipments_stats.html", {})


@login_required()
def api_return_shipments_stats(request) -> JsonResponse:
    """Return the article stats as JSON."""
    start_date = request.GET.get("start")
    if not start_date:
        start_date = date.today() - timedelta(weeks=4)

    end_date = request.GET.get("end")
    if not end_date:
        end_date = date.today()

    marketplace = request.GET.get("marketplace")
    if not marketplace:
        return JsonResponse(
            {
                "status": "false",
                "message": "No marketplace name - do you know what you are doing?",
            },
            status=500,
        )

    article_stats = get_article_stats(marketplace, start_date, end_date)

    return JsonResponse(article_stats, safe=False)
