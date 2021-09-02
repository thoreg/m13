from django.db import models
from django_extensions.db.models import TimeStampedModel


class FeedUpload(TimeStampedModel):
    """Track when we did which feed upload."""
    status_code_validation = models.PositiveSmallIntegerField()
    status_code_feed_upload = models.PositiveSmallIntegerField()
    number_of_valid_items = models.PositiveIntegerField()
    path_to_original_csv = models.CharField(max_length=128)
    path_to_pimped_csv = models.CharField(max_length=128)
