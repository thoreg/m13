import csv
import datetime as dt
import json
import logging
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from pprint import pformat, pprint
from secrets import compare_digest

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic, non_atomic_requests
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from zalando.services.prices import update_z_factor

from .forms import PriceToolForm, UploadFileForm
from .models import (FeedUpload, OEAWebhookMessage, OrderItem, PriceTool, Product, StatsOrderItems,
                     TransactionFileUpload)

LOG = logging.getLogger(__name__)


@login_required
def price_feed(request):
    """Price Feed Index View."""
    feed_uploads = FeedUpload.objects.all().order_by('-created')[:5]

    if request.method == 'POST':
        form = PriceToolForm(request.POST)
        if form.is_valid():
            update_z_factor(form.cleaned_data['z_factor'])
            return HttpResponseRedirect(reverse('zalando_index'))
    else:
        form = PriceToolForm()

    try:
        price_tool = PriceTool.objects.get(active=True)
        z_factor = price_tool.z_factor
    except PriceTool.DoesNotExist:
        z_factor = 'UNDEFINED'

    ctx = {
        'feed_uploads': feed_uploads,
        'form': form,
        'z_factor': z_factor,
    }
    return render(request, 'zalando/price_feed.html', ctx)


@login_required
def index(request):
    """Zalando Index View."""
    order_items = (
        OrderItem.objects.all()
        .order_by('-order__order_date')
        .select_related('order__delivery_address')[:100]
    )
    products = {p['ean']: p['title'] for p in Product.objects.all().values()}
    ctx = {
        'dbyesterday': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
        'yesterday': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        'today': datetime.now().strftime('%Y-%m-%d'),
        'order_items': order_items,
        'products': products,
    }
    LOG.info(ctx)
    return render(request, 'zalando/index.html', ctx)


@csrf_exempt
@require_POST
@non_atomic_requests
def oea_webhook(request):
    """Handle incoming webhook messages."""
    if not settings.ZALANDO_OEM_WEBHOOK_TOKEN:
        return HttpResponse('Token not defined.', content_type='text/plain')

    given_token = request.headers.get('x-api-key', '')
    if not compare_digest(given_token, settings.ZALANDO_OEM_WEBHOOK_TOKEN):
        return HttpResponseForbidden(
            'Incorrect token in header',
            content_type='text/plain'
        )

    OEAWebhookMessage.objects.filter(
        created__lte=timezone.now() - dt.timedelta(days=365)
    ).delete()

    try:
        payload = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        LOG.exception('JSON decode failed')
        LOG.error(request.body)
        return HttpResponse(
            'Request body is not JSON', content_type='text/plain')

    OEAWebhookMessage.objects.create(payload=payload)
    process_oea_webhook_payload(payload)
    return HttpResponse('Message received okay.', content_type='text/plain')


@atomic
def process_oea_webhook_payload(payload):
    LOG.info(payload)


@login_required
def orderitems_csv(request, day):
    """Return all processible orderitems as csv."""

    LOG.info(request.__dict__)
    LOG.info(f'GET: {request.GET.__dict__}')
    LOG.info(f'day: {day}')

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{date}.csv"'},
    )

    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Bestellnummer',
        'Vorname',
        'Name',
        'Straße',
        'PLZ',
        'Ort',
        'Land',
        'Artikelnummer',
        'Artikelname',
        'Preis (Brutto)',
        'Menge',
        'Positionstyp',
        'Anmerkung',
        'EMAIL'
    ])

    return response


@login_required
def stats_orderitems(request):
    return JsonResponse(
        list(StatsOrderItems.objects.all().values()), safe=False)


@login_required
def upload_files(request):
    """Handle for uploaded files."""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist('original_csv')
        if form.is_valid():
            month = form['month'].value()
            for f in files:
                handle_uploaded_file(month, f)
            context = {'msg': '<span style="color: green;">File successfully uploaded</span>'}
            return render(request, 'zalando/finance/upload.html', context)
    else:
        form = UploadFileForm()
    return render(request, 'zalando/finance/upload.html', {'form': form})


def handle_uploaded_file(month, f):
    """Handle for single uploaded file."""
    if not settings.ZALANDO_FINANCE_CSV_UPLOAD_PATH:
        return HttpResponse(
            'ZALANDO_FINANCE_CSV_UPLOAD_PATH not defined.', content_type='text/plain')

    directory = os.path.join(settings.ZALANDO_FINANCE_CSV_UPLOAD_PATH, month[:4], month[4:],)
    Path(directory).mkdir(parents=True, exist_ok=True)

    path = os.path.join(directory, f.name)
    print(f'path: {path}')
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        TransactionFileUpload.objects.create(
            status_code_upload=True,
            status_code_processing=False,
            original_csv=path,
            month=month
        )
