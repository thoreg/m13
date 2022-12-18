from rest_framework import permissions, viewsets

from otto.models import OrderItem

from .serializers import OrderItemSerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to download order items.
    """

    # queryset = OrderItem.objects.all().order_by('-date_joined')
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
