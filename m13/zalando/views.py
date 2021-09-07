import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import PriceToolForm
from .models import FeedUpload, PriceTool
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
