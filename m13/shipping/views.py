from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from etsy.models import Shipment as EtsyShipment
from etsy.services.shipments import handle_uploaded_file as etsy_handle_upload
from otto.models import Shipment as OttoShipment
from otto.services.shipments import handle_uploaded_file as otto_handle_upload

from .forms import UploadFileForm


@login_required
def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            otto_handle_upload(file)
            file.open()
            etsy_handle_upload(file)
            return HttpResponseRedirect(reverse('upload_shipping_infos_success'))
    else:
        form = UploadFileForm()
    return render(request, 'shipping/index.html', {'form': form})


@login_required
def upload_shipping_infos_success(request):
    otto_shipments = OttoShipment.objects.all().order_by('-created')[:200]
    etsy_shipments = EtsyShipment.objects.all().order_by('-created')[:100]
    return render(
        request, 'shipping/upload_success.html', {
            'otto_shipments': otto_shipments,
            'etsy_shipments': etsy_shipments,
        })
