from rest_framework import serializers

from zalando.models import ZProduct


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
            'vk_zalando',
        )
        read_only_fields = (
            'eight_percent_provision',
            'generic_costs',
            'nineteen_percent_vat',
            'profit_after_taxes'
        )
