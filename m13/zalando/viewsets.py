from datetime import date

import django_filters.rest_framework
from django.http import HttpResponse
from rest_framework import generics

from .models import RawDailyShipmentReport, ZProduct
from .serializers import RawDailyShipmentReportSerializer, ZProductSerializer


class ZProductList(generics.ListCreateAPIView):
    queryset = ZProduct.objects.all().order_by('-shipped')
    serializer_class = ZProductSerializer


class ZProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ZProduct.objects.all()
    serializer_class = ZProductSerializer


class RawDailyShipmentReportList(generics.ListAPIView):
    serializer_class = RawDailyShipmentReportSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def get_queryset(self):
        """..."""
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date and not end_date:
            today = date.today()
            return RawDailyShipmentReport.objects.filter(
                order_event_time__range=(start_date, today))

        if start_date and end_date:
            return RawDailyShipmentReport.objects.filter(
                order_event_time__range=(start_date, end_date))

        return RawDailyShipmentReport.objects.all()
