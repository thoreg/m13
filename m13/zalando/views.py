import logging
import datetime as dt
import json
from secrets import compare_digest

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.transaction import non_atomic_requests, atomic
from django.utils import timezone

from .forms import PriceToolForm
from .models import FeedUpload, PriceTool, OEAWebhookMessage
from .services import update_z_factor

LOG = logging.getLogger(__name__)


@login_required
def index(request):
    LOG.info('welcome at zalando index')
    feed_uploads = FeedUpload.objects.all().order_by('-created')[:13]

    if request.method == 'POST':
        LOG.info('form is valid')
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
        'z_factor': z_factor,
        'feed_uploads': feed_uploads,
        'form': form
    }

    return render(request, 'zalando/index.html', ctx)


@csrf_exempt
@require_POST
@non_atomic_requests
def oea_webhook(request):
    if not settings.ZALANDO_OEM_WEBHOOK_TOKEN:
        return HttpResponse('Token not defined.', content_type='text/plain')

    given_token = request.headers.get('x-api-key', '')
    if not compare_digest(given_token, settings.ZALANDO_OEM_WEBHOOK_TOKEN):
        return HttpResponseForbidden(
            'Incorrect token in header',
            content_type='text/plain'
        )

    OEAWebhookMessage.objects.filter(
        created__lte=timezone.now() - dt.timedelta(days=7)
    ).delete()

    payload = json.loads(request.body)
    OEAWebhookMessage.objects.create(payload=payload)
    process_oea_webhook_payload(payload)
    return HttpResponse('Message received okay.', content_type='text/plain')


@atomic
def process_oea_webhook_payload(payload):
    LOG.info(payload)
