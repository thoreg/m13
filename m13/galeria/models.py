from django.db import models
from django_extensions.db.models import TimeStampedModel


class FeedUpload(TimeStampedModel):
    """Track when we did which feed upload/creation."""

    path_to_original_csv = models.CharField(max_length=128)
    path_to_pimped_csv = models.CharField(max_length=128)
    path_to_pimped_xlsx = models.CharField(max_length=128)
