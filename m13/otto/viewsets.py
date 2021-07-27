from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import OrderItemSerializer
from otto.models import OrderItem


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to download order items.
    """
    # queryset = OrderItem.objects.all().order_by('-date_joined')
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]