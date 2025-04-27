from django.db import models
from django_extensions.db.models import TimeStampedModel


class BatchRequest(TimeStampedModel):
    """Track batch requests (e.g. stock updates)."""

    id = models.CharField(primary_key=True)
    started = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, null=True)
    completed = models.DateTimeField(null=True)
