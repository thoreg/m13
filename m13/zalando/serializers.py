from rest_framework import serializers

from zalando.models import ZProduct


class ZProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = ZProduct
        fields = '__all__'
