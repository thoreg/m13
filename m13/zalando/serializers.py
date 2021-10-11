from rest_framework import serializers

from zalando.models import FeedRow


class FeedRowSerializer(serializers.HyperlinkedModelSerializer):
    store = serializers.CharField()
    ean = serializers.CharField()
    title = serializers.CharField()
    price = serializers.CharField()
    quantity = serializers.IntegerField()
    article_number = serializers.CharField()
    color = serializers.CharField()
    price_overwrite = serializers.CharField()
    use_row = serializers.BooleanField()

    class Meta:
        model = FeedRow
        fields = '__all__'
