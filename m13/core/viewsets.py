from rest_framework import permissions, viewsets

from .models import SalesStatsTop13, SalesStatsReturnTop13

from .serializers import SalesStatsTop13Serializer, SalesStatsReturnTop13Serializer


class SalesStatsTop13ViewSet(viewsets.ModelViewSet):
    """API endpoint to receive top sales by sku."""
    queryset = SalesStatsTop13.objects.all()
    serializer_class = SalesStatsTop13Serializer
    permission_classes = [permissions.IsAuthenticated]


class SalesStatsTop13ReturnViewSet(viewsets.ModelViewSet):
    """API endpoint to receive top sales by sku."""
    queryset = SalesStatsReturnTop13.objects.all()
    serializer_class = SalesStatsReturnTop13Serializer
    permission_classes = [permissions.IsAuthenticated]
