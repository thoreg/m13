"""Get just the fields from a datadump."""

import json

from django.core import serializers
from django.core.management.base import BaseCommand

from core.models import Category, Price


class Command(BaseCommand):
    """..."""

    def handle(self, *args, **kwargs):
        """..."""
        data = serializers.serialize("json", Price.objects.all())
        data_as_list_of_dicts = json.loads(data)
        data = [d["fields"] for d in data_as_list_of_dicts]

        with open("prices.json", "wt") as output:
            json.dump(data, output)

        data = serializers.serialize("json", Category.objects.all())
        data_as_list_of_dicts = json.loads(data)
        data = [d["fields"] for d in data_as_list_of_dicts]

        with open("category.json", "wt") as output:
            json.dump(data, output)
