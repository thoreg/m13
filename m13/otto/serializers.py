from otto.models import OrderItem
from rest_framework import serializers


class OrderItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['ean', 'product_title']