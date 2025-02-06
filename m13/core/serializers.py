from rest_framework import serializers

from .models import SalesStatsReturnTop13, SalesStatsTop13


class SalesStatsTop13Serializer(serializers.HyperlinkedModelSerializer):
    """..."""

    class Meta:
        """..."""

        model = SalesStatsTop13
        fields = [
            "sku",
            "category_name",
            "shipped",
        ]


class SalesStatsReturnTop13Serializer(serializers.HyperlinkedModelSerializer):
    """..."""

    class Meta:
        """..."""

        model = SalesStatsReturnTop13
        fields = [
            "sku",
            "category_name",
            "returned",
        ]
