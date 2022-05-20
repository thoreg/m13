import csv
import datetime as dt
import json
import logging
from datetime import date, datetime, timedelta
from secrets import compare_digest

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Count
from django.db.transaction import atomic, non_atomic_requests
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from m13.lib.file_upload import handle_uploaded_file
from m13.lib.psql import dictfetchall
from zalando.services.prices import update_z_factor

from .forms import PriceToolForm, UploadFileForm
from .models import (FeedUpload, OEAWebhookMessage, OrderItem, PriceTool,
                     Product, StatsOrderItems, TransactionFileUpload)

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
    """Return order items stats in JSON format."""
    return JsonResponse(
        list(StatsOrderItems.objects.all().values()), safe=False)


@login_required
def upload_files(request):
    """Handle for uploaded files."""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist('original_csv')
        if form.is_valid():
            for f in files:
                path = handle_uploaded_file(settings.ZALANDO_FINANCE_CSV_UPLOAD_PATH, f)
                _tfu, created = TransactionFileUpload.objects.get_or_create(
                    file_name=f.name, defaults={
                        'original_csv': path,
                        'processed': False,
                    })
                if created:
                    LOG.info(f'{path} successfully uploaded')
                else:
                    LOG.info(f'{path} already exist')

            context = {'msg': f'{len(files)} files uploaded successfully'}
            return render(request, 'zalando/finance/upload.html', context)

        context = {'msg': 'Form is invalid'}
        return render(request, 'zalando/finance/upload.html', context)
    else:
        form = UploadFileForm()

    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT
                article_number,
                COUNT(shipment) FILTER (WHERE shipment) AS shipped,
                COUNT(returned) FILTER (WHERE returned) AS returned,
                COUNT(cancel) FILTER (WHERE cancel) AS canceled
            FROM
                zalando_dailyshipmentreport
            GROUP BY
                article_number
            ORDER BY
                returned DESC
        ''')
        article_stats = dictfetchall(cursor)

    return render(request, 'zalando/finance/upload.html', {
        'article_stats': article_stats,
        'form': form
    })
