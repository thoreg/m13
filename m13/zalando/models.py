from django.db import models
from django_extensions.db.models import TimeStampedModel


class FeedUpload(TimeStampedModel):
    """Track when we did which feed upload."""
    status_code_validation = models.PositiveSmallIntegerField()
    status_code_feed_upload = models.PositiveSmallIntegerField()
    number_of_valid_items = models.PositiveIntegerField()
    path_to_original_csv = models.CharField(max_length=128)
    path_to_pimped_csv = models.CharField(max_length=128)
    z_factor = models.DecimalField(max_digits=3, decimal_places=2)


class PriceTool(TimeStampedModel):
    z_factor = models.DecimalField(max_digits=3, decimal_places=2)
    active = models.BooleanField(default=False)


class OEAWebhookMessage(TimeStampedModel):
    """Order Event API Message."""
    payload = models.JSONField(default=None, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['created']),
        ]
