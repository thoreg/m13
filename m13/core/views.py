import csv
import logging
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from core.models import Price

from .services.article_stats import get_article_stats

LOG = logging.getLogger(__name__)


@login_required
def return_shipments_stats(request):
    """Overview of 'the calculator'.

    Shows stats about shipped vs returned orderitem ratio over several
    marketplaces.

    """
    return render(
        request,
        "core/return_shipments_stats.html",
        {
            "location": "calculator",
        },
    )


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
    article_keys = list(article_stats.keys())
    article_keys.sort()
    sorted_article_stats = {i: article_stats[i] for i in article_keys}

    return JsonResponse(sorted_article_stats, safe=False)


def sku_production_costs(request):
    """Return the sku production costs."""
    prices = Price.objects.filter(costs_production__isnull=False).values_list(
        "sku", "costs_production"
    )

    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="m13_production_costs.csv"'
        },
    )

    writer = csv.writer(response)
    writer.writerow(["sku", "costs_production"])
    for sku, costs in prices:
        print(f"SKU: {sku}, Production Costs: {costs}")
        writer.writerow([sku, costs])

    return response
