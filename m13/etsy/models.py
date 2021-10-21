from django.db import models
from django_extensions.db.models import TimeStampedModel


class OAuth(TimeStampedModel):
    """Store token + refresh token."""
    token = models.TextField()
    token_secret = models.TextField()
    refresh_token = models.TextField()
