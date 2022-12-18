from rest_framework import permissions, viewsets

from .models import OrderItem
from .serializers import OrderItemSerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to download order items.
    """

    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
