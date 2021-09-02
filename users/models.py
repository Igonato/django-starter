from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model"""
    is_verified = models.BooleanField(_('email verified'), default=False)
    oauth = models.JSONField(_('OAuth 2.0 data'), blank=True, null=True)
