import csv
import datetime as dt
import json
import logging
from datetime import date, datetime, timedelta
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

from m13.lib.file_upload import handle_uploaded_file
from zalando.services.daily_shipment_reports import import_daily_shipment_report
from zalando.services.prices import update_z_factor

from .forms import PriceToolForm, UploadFileForm
from .models import (FeedUpload, OEAWebhookMessage, OrderItem, PriceTool, Product, StatsOrderItems,
                     TransactionFileUpload, ZProduct)
from .services import daily_shipment_reports

LOG = logging.getLogger(__name__)

MAX_LENGTH_CATEGORY = 18


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
                tfu, created = TransactionFileUpload.objects.get_or_create(
                    file_name=f.name, defaults={
                        'original_csv': path,
                        'processed': False,
                    })
                import_daily_shipment_report(tfu)

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

    file_uploads = TransactionFileUpload.objects.all().order_by('-created')[:50]
    LOG.info(f'we have {len(file_uploads)} objects')

    return render(request, 'zalando/finance/upload.html', {
        'file_uploads': file_uploads,
        'form': form
    })


@login_required
def calculator(request):
    """Overview of all zalando calculator values."""
    return render(request, 'zalando/finance/z_calculator.html', {})


@login_required()
def article_stats(request):
    """Return the article stats as JSON."""
    return JsonResponse(daily_shipment_reports.get_product_stats(), safe=False)


@login_required
def calculator_v1(request):
    """Overview of all zalando calculator values."""
    return render(request, 'zalando/finance/z_calculator_v1.html', {})


@login_required()
def product_stats_v1(request):
    """Return the article stats as JSON."""
    start_date = request.GET.get('start')
    if not start_date:
        start_date = date.today() - timedelta(weeks=4)

    zproducts = ZProduct.objects.select_related('category').all()
    LOG.info(f'Found {len(zproducts)} zproducts')

    zproduct_by_sku = {}
    for zp in zproducts:
        zproduct_by_sku[zp.article] = {
            'category': zp.category.name if zp.category else 'N/A',
            'costs_production': zp.costs_production,
            'eight_percent_provision': zp.eight_percent_provision,
            'generic_costs': zp.generic_costs,
            'nineteen_percent_vat': zp.nineteen_percent_vat,
            'profit_after_taxes': zp.profit_after_taxes,
            'return_costs': zp.return_costs,
            'shipping_costs': zp.shipping_costs,
            'vk_zalando': zp.vk_zalando
        }

    product_shipping_stats = daily_shipment_reports.get_product_stats_v1(start_date)
    LOG.info(f'Got {len(product_shipping_stats)} product shipping stats entries')

    for pss in product_shipping_stats:
        sku = pss['article_number']
        try:
            pss.update({
                'category': zproduct_by_sku[sku]['category'],
                'costs_production': zproduct_by_sku[sku]['costs_production'],
                'eight_percent_provision': zproduct_by_sku[sku]['eight_percent_provision'],
                'generic_costs': zproduct_by_sku[sku]['generic_costs'],
                'nineteen_percent_vat': zproduct_by_sku[sku]['nineteen_percent_vat'],
                'profit_after_taxes': zproduct_by_sku[sku]['profit_after_taxes'],
                'return_costs': zproduct_by_sku[sku]['return_costs'],
                'shipping_costs': zproduct_by_sku[sku]['shipping_costs'],
                'vk_zalando': zproduct_by_sku[sku]['vk_zalando']
            })
        except KeyError:
            LOG.exception(f'sku: {sku} not in zproduct?')

    pss_by_category = {}
    for pss in product_shipping_stats:
        try:
            category = pss['category']
        except KeyError:
            LOG.exception('no category in pss')
            LOG.error(pss)
            continue

        category = pss['category'][:MAX_LENGTH_CATEGORY]
        if category not in pss_by_category:
            pss_by_category[category] = {
                'name': category,
                'stats': {
                    'shipped': pss['shipped'],
                    'returned': pss['returned'],
                    'canceled': pss['canceled'],
                    'total_revenue': 0,
                    'total_return_costs': 0,
                    'total_diff': 0,
                },
                'content': [pss]
            }
        else:
            pss_by_category[category]['stats']['shipped'] += pss['shipped']
            pss_by_category[category]['stats']['returned'] += pss['returned']
            pss_by_category[category]['stats']['canceled'] += pss['canceled']
            pss_by_category[category]['content'].append(pss)

        if pss['vk_zalando']:
            # Update product (specific) shipping stats (psss)
            pss['total_revenue'] = (
                pss['profit_after_taxes'] * (pss['shipped'] - pss['returned'])
            )
            pss['total_return_costs'] = (
                pss['returned'] * (
                    pss['shipping_costs'] + pss['return_costs'] + pss['generic_costs'])
            )
            pss['total_diff'] = pss['total_revenue'] - pss['total_return_costs']

            # Update category (specific) shipping stats (csss)
            pss_by_category[category]['stats']['total_revenue'] = (
                pss['profit_after_taxes'] * (
                    pss_by_category[category]['stats']['shipped']
                    - pss_by_category[category]['stats']['returned']
                )
            )
            pss_by_category[category]['stats']['total_return_costs'] = (
                pss_by_category[category]['stats']['returned'] * (
                    pss['shipping_costs']
                    + pss['return_costs']
                    + pss['generic_costs']
                )
            )
            pss_by_category[category]['stats']['total_diff'] = (
                pss_by_category[category]['stats']['total_revenue']
                - pss_by_category[category]['stats']['total_return_costs']
            )

    LOG.info(f'Got {len(pss_by_category)} pss_by_category entries')
    return JsonResponse(pss_by_category, safe=False)
