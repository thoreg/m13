import csv
import datetime as dt
import json
import logging
from datetime import date, timedelta
from secrets import compare_digest

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic, non_atomic_requests
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from m13.lib import log as mlog
from m13.lib.file_upload import handle_uploaded_file
from zalando.models import SalesReportFileUpload
from zalando.services.prices import update_z_factor
from zalando.services.reports import import_monthly_sales_report

from .forms import PriceToolForm, UploadFileForm
from .models import (
    FeedUpload,
    OEAWebhookMessage,
    OrderItem,
    PriceTool,
    Product,
    StatsOrderItems,
)

LOG = logging.getLogger(__name__)

MAX_LENGTH_CATEGORY = 18
LOCATION = "zalando"


@login_required
def price_feed(request):
    """Price Feed Index View."""
    feed_uploads = FeedUpload.objects.all().order_by("-created")[:5]

    if request.method == "POST":
        form = PriceToolForm(request.POST)
        if form.is_valid():
            update_z_factor(form.cleaned_data["z_factor"])
            return HttpResponseRedirect(reverse("zalando_index"))
    else:
        form = PriceToolForm()

    try:
        price_tool = PriceTool.objects.get(active=True)
        z_factor = price_tool.z_factor
    except PriceTool.DoesNotExist:
        z_factor = "UNDEFINED"

    ctx = {
        "feed_uploads": feed_uploads,
        "form": form,
        "z_factor": z_factor,
        "location": LOCATION,
    }
    return render(request, "zalando/price_feed.html", ctx)


@login_required
def index(request):
    """Zalando Index View."""
    order_items = (
        OrderItem.objects.all()
        .order_by("-order__order_date")
        .select_related("order__delivery_address")[:100]
    )
    products = {p["ean"]: p["title"] for p in Product.objects.all().values()}
    ctx = {
        "dbyesterday": (timezone.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "yesterday": (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "today": timezone.now().strftime("%Y-%m-%d"),
        "order_items": order_items,
        "products": products,
        "location": LOCATION,
    }
    LOG.info(ctx)
    return render(request, "zalando/index.html", ctx)


@csrf_exempt
@require_POST
@non_atomic_requests
def oea_webhook(request):
    """Handle incoming webhook messages."""
    if not settings.ZALANDO_OEM_WEBHOOK_TOKEN:
        return HttpResponse("Token not defined.", content_type="text/plain")

    given_token = request.headers.get("x-api-key", "")
    if not compare_digest(given_token, settings.ZALANDO_OEM_WEBHOOK_TOKEN):
        return HttpResponseForbidden(
            "Incorrect token in header", content_type="text/plain"
        )

    OEAWebhookMessage.objects.filter(
        created__lte=timezone.now() - dt.timedelta(days=365)
    ).delete()

    try:
        payload = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        LOG.exception("JSON decode failed")
        mlog.error(LOG, request.body)
        return HttpResponse("Request body is not JSON", content_type="text/plain")

    OEAWebhookMessage.objects.create(payload=payload)
    process_oea_webhook_payload(payload)
    return HttpResponse("Message received okay.", content_type="text/plain")


@atomic
def process_oea_webhook_payload(payload):
    LOG.info(payload)


@login_required
def orderitems_csv(request, day):
    """Return all processible orderitems as csv."""

    LOG.info(request.__dict__)
    LOG.info(f"GET: {request.GET.__dict__}")
    LOG.info(f"day: {day}")

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{date}.csv"'},
    )

    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [
            "Bestellnummer",
            "Vorname",
            "Name",
            "Straße",
            "PLZ",
            "Ort",
            "Land",
            "Artikelnummer",
            "Artikelname",
            "Preis (Brutto)",
            "Menge",
            "Positionstyp",
            "Anmerkung",
            "EMAIL",
        ]
    )

    return response


@login_required
def stats_orderitems(request):
    """Return order items stats in JSON format."""
    return JsonResponse(list(StatsOrderItems.objects.all().values()), safe=False)


@login_required
def upload_files(request):
    """Handle for uploaded files."""
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist("original_csv")
        if form.is_valid():
            for f in files:
                # Check if the csv file is already known - we need to
                # prevent duplicate uploads which would lead to duplicate
                # inserts (all entries of the file are inserted)
                try:
                    SalesReportFileUpload.objects.get(file_name=f.name)
                    msg = f"{f.name} is already imported - skipping"
                    LOG.info(msg)
                    messages.error(request, msg)
                    return redirect(reverse("zalando_finance_upload_files"))

                except SalesReportFileUpload.DoesNotExist:
                    pass

                path = handle_uploaded_file(settings.ZALANDO_FINANCE_CSV_UPLOAD_PATH, f)
                srfu, created = SalesReportFileUpload.objects.get_or_create(
                    file_name=f.name,
                    defaults={
                        "original_csv": path,
                        "processed": False,
                    },
                )
                import_monthly_sales_report(srfu)

                if created:
                    LOG.info(f"{path} successfully uploaded")
                else:
                    LOG.info(f"{path} already exist")

            msg = f"{len(files)} files uploaded successfully"
            messages.success(request, msg)
            return redirect(reverse("zalando_finance_upload_files"))

        context = {
            "msg": "Form is invalid",
            "location": LOCATION,
        }
        return render(request, "zalando/finance/upload.html", context)
    else:
        form = UploadFileForm()

    file_uploads = SalesReportFileUpload.objects.all().order_by("-created")[:50]
    LOG.info(f"we have {len(file_uploads)} objects")

    return render(
        request,
        "zalando/finance/upload.html",
        {
            "file_uploads": file_uploads,
            "form": form,
            "location": LOCATION,
        },
    )


@login_required
def calculator_v1(request):
    """Overview of all zalando calculator values."""
    return render(
        request,
        "zalando/finance/z_calculator_v1.html",
        {
            "location": LOCATION,
        },
    )
