from rest_framework import serializers

from zalando.models import RawDailyShipmentReport, ZProduct


class ZProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = ZProduct
        fields = (
            'article',
            'canceled',
            'category_name',
            'costs_production',
            'eight_percent_provision',
            'generic_costs',
            'nineteen_percent_vat',
            'profit_after_taxes',
            'return_costs',
            'returned',
            'shipped',
            'shipping_costs',
            'total_revenue',
            'total_return_costs',
            'total_diff',
            'vk_zalando',
        )
        read_only_fields = (
            'eight_percent_provision',
            'generic_costs',
            'nineteen_percent_vat',
            'profit_after_taxes',
            'total_revenue',
            'total_return_costs',
            'total_diff',
        )


class RawDailyShipmentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawDailyShipmentReport
        fields = (
            'article_number',
            'cancel',
            'channel_order_number',
            # 'category_name',
            'order_created',
            'order_event_time',
            'price_in_cent',
            'return_reason',
            'returned',
            'shipment',
        )
