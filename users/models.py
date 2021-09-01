from django.contrib.auth import login
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from rest_registration.signals import user_registered


class User(AbstractUser):
    """Custom User model"""
    is_verified = models.BooleanField(_('email verified'), default=False)


@receiver(user_registered, sender=None)
def auto_login_on_registration(user, request, **kwargs):
    login(request, user)
