from django.conf import settings

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app', )

if settings.DEBUG:
    # Clear cache on reloading when DEBUG is True
    from django.core.cache import cache
    cache.clear()
