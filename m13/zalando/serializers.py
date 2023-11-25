from rest_framework import serializers

from zalando.models import RawDailyShipmentReport


class RawDailyShipmentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawDailyShipmentReport
        fields = (
            "article_number",
            "cancel",
            "channel_order_number",
            # 'category_name',
            "order_created",
            "order_event_time",
            "price_in_cent",
            "return_reason",
            "returned",
            "shipment",
        )
