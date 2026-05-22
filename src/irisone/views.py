import csv
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import FeedUpload, Order, OrderLine

LOG = logging.getLogger(__name__)

LOCATION = "irisone"


@login_required
def index(request):
    """irisOne order overview."""
    orders = Order.objects.all().order_by("-order_date").prefetch_related("lines")[:100]
    ctx = {
        "orders": orders,
        "location": LOCATION,
    }
    return render(request, "irisone/index.html", ctx)


@login_required
def feed(request):
    """irisOne feed upload overview."""
    feed_uploads = FeedUpload.objects.all().order_by("-created")[:5]
    ctx = {
        "feed_uploads": feed_uploads,
        "location": LOCATION,
    }
    return render(request, "irisone/feed.html", ctx)


@login_required
def orders_csv(request):
    """Download all open orders as CSV file."""
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="irisone_orders_{timezone.now().strftime("%Y%m%d")}.csv"'
            )
        },
    )
    response.write("﻿".encode("utf8"))

    writer = csv.writer(response, delimiter=";")
    writer.writerow([
        "booking_id",
        "order_id",
        "marketplace",
        "marketplace_order_id",
        "order_date",
        "status",
        "line_id",
        "article_number",
        "sku",
        "price",
        "line_status",
    ])

    lines = (
        OrderLine.objects.select_related("order")
        .filter(order__status__in=[Order.Status.PENDING, Order.Status.OPENED])
        .order_by("order__order_date")
    )

    for line in lines:
        order = line.order
        writer.writerow([
            order.booking_id,
            order.order_id,
            order.marketplace_name,
            order.marketplace_order_id_1,
            order.order_date.strftime("%Y-%m-%d %H:%M"),
            order.status,
            line.line_id,
            line.article_number,
            line.marketplace_sku,
            line.price,
            line.status,
        ])

    return response
