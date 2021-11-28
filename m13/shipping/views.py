import logging
from copy import deepcopy

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from etsy.models import Shipment as EtsyShipment
from etsy.services.shipments import handle_uploaded_file as etsy_handle_upload
from otto.models import Shipment as OttoShipment
from otto.services.shipments import handle_uploaded_file as otto_handle_upload

from .forms import UploadFileForm

LOG = logging.getLogger(__name__)


@login_required
def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file1 = deepcopy(request.FILES['file'])
            file2 = deepcopy(request.FILES['file'])
            otto_handle_upload(file1)
            etsy_handle_upload(file2)
            return HttpResponseRedirect(reverse('upload_shipping_infos_success'))
    else:
        form = UploadFileForm()
    return render(request, 'shipping/index.html', {'form': form})


@login_required
def upload_shipping_infos_success(request):
    otto_shipments = OttoShipment.objects.all().order_by('-created')[:200]
    etsy_shipments = EtsyShipment.objects.all().order_by('-created')[:100]
    LOG.info(f'otto_shipments: {len(otto_shipments)}')
    LOG.info(f'etsy_shipments: {len(etsy_shipments)}')
    return render(
        request, 'shipping/upload_success.html', {
            'otto_shipments': otto_shipments,
            'etsy_shipments': etsy_shipments,
        })
