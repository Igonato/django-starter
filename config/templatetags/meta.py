from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def meta(key):
    return settings.META.get(key, '')
