import logging
from copy import deepcopy

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from aboutyou.models import Shipment as AboutYouShipment
from aboutyou.services.shipments import handle_uploaded_file as ay_handle_upload
from etsy.models import Shipment as EtsyShipment
from etsy.services.shipments import handle_uploaded_file as etsy_handle_upload
from otto.models import Shipment as OttoShipment
from otto.services.shipments import handle_uploaded_file as otto_handle_upload
from tiktok.models import Shipment as TiktokShipment
from tiktok.services.shipments import handle_uploaded_file as tiktok_handle_upload

from .forms import UploadFileForm

LOG = logging.getLogger(__name__)
LOCATION = "shipping"


@login_required
def index(request):
    """..."""
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file1 = deepcopy(request.FILES["file"])
            file2 = deepcopy(request.FILES["file"])
            file3 = deepcopy(request.FILES["file"])
            file4 = deepcopy(request.FILES["file"])

            otto_handle_upload(file1)
            etsy_handle_upload(file2)
            tiktok_handle_upload(file3)
            ay_handle_upload(file4)

            return HttpResponseRedirect(reverse("upload_shipping_infos_success"))
    else:
        form = UploadFileForm()
    return render(
        request,
        "shipping/index.html",
        {
            "form": form,
            "location": LOCATION,
        },
    )


@login_required
def upload_shipping_infos_success(request):
    """..."""
    otto_shipments = (
        OttoShipment.objects.all()
        .order_by("-created")
        .values_list(
            "created",
            "order__marketplace_order_number",
            "carrier",
            "tracking_info",
            "response_status_code",
        )[:100]
    )
    etsy_shipments = (
        EtsyShipment.objects.all()
        .order_by("-created")
        .values_list(
            "created",
            "order__marketplace_order_id",
            "carrier",
            "tracking_info",
            "response_status_code",
        )[:100]
    )
    tiktok_shipments = (
        TiktokShipment.objects.all()
        .order_by("-created")
        .values_list(
            "created",
            "package_id",
            "tracking_number",
            "response_status_code",
        )[:100]
    )
    return render(
        request,
        "shipping/upload_success.html",
        {
            "etsy_shipments": etsy_shipments,
            "otto_shipments": otto_shipments,
            "tiktok_shipments": tiktok_shipments,
            "location": LOCATION,
        },
    )
