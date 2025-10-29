from datetime import date, timedelta

import django_filters.rest_framework
from rest_framework import viewsets as drf_viewsets

from .models import RawDailyShipmentReport
from .serializers import RawDailyShipmentReportSerializer


class RawDailyShipmentReportList(drf_viewsets.ModelViewSet):
    filterset_fields = {
        "order_event_time": ["gte", "gt", "lte", "lt"],
    }
    queryset = RawDailyShipmentReport.objects.all().order_by("-created")
    serializer_class = RawDailyShipmentReportSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def get_queryset(self):
        """..."""
        start_date = self.request.GET.get("order_event_time__gte")
        today = date.today()

        if not start_date:
            start_date = today - timedelta(weeks=4)

        return RawDailyShipmentReport.objects.filter(
            order_event_time__range=(start_date, today)
        )
