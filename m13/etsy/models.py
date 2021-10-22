from django.db import models
from django_extensions.db.models import TimeStampedModel


class OAuth(TimeStampedModel):
    """Store token + refresh token."""
    token = models.TextField()
    token_secret = models.TextField()
    refresh_token = models.TextField()


class AuthRequest(TimeStampedModel):
    verifier = models.BinaryField(max_length=256)
    code_challenge = models.BinaryField(max_length=128)
    state = models.CharField(max_length=8)
    auth_code = models.CharField(max_length=128, null=True, blank=True)
    auth_token = models.CharField(max_length=128, null=True, blank=True)


class AuthRequest2(TimeStampedModel):
    verifier = models.CharField(max_length=512)
    code_challenge = models.CharField(max_length=256)
    state = models.CharField(max_length=8)
    auth_token = models.CharField(max_length=128, null=True, blank=True)
    refresh_token = models.CharField(max_length=128, null=True, blank=True)
