from otto.models import OrderItem
from rest_framework import serializers


class OrderItemSerializer(serializers.HyperlinkedModelSerializer):
    marketplace_order_number = serializers.CharField(
        source='order.marketplace_order_number')
    first_name = serializers.CharField(
        source='order.delivery_address.first_name')
    last_name = serializers.CharField(
        source='order.delivery_address.last_name')
    street = serializers.CharField(
        source='order.delivery_address.street')
    house_number = serializers.CharField(
        source='order.delivery_address.house_number')
    zip_code = serializers.CharField(
        source='order.delivery_address.zip_code')
    city = serializers.CharField(
        source='order.delivery_address.city')
    country_code = serializers.CharField(
        source='order.delivery_address.country_code')

    # Menge ?
    # Positionstyp?

    class Meta:
        model = OrderItem
        fields = [
            'marketplace_order_number',
            'first_name',
            'last_name',
            'street',
            'house_number',
            'zip_code',
            'city',
            'country_code',
            'sku',
            'product_title',
            'price_in_cent',
        ]