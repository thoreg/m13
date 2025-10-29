"""Remove all job results wich are older then X days."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Job
from m13.lib.common import monitor

MAX_AGAE_IN_HOURS = 48


class Command(BaseCommand):
    help = "Remove all job results wich are older then X days."

    @monitor
    def handle(self, *args, **kwargs):
        """..."""
        two_days_ago = timezone.now() - timedelta(hours=MAX_AGAE_IN_HOURS)
        Job.objects.filter(created__lt=two_days_ago).delete()
        return 0
