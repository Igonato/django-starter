from http import HTTPStatus

from django.conf import settings
from django.template import Context, Template

from rest_framework.reverse import reverse

from .celery import debug_task


def test_celery_task(celery_worker):
    assert debug_task.delay().get(timeout=5) is None


def test_meta_template_tag(client):
    template = Template('{% load meta %}{% meta "NAME" %}')
    rendered = template.render(Context({}))
    assert rendered == settings.META['NAME']


def test_api_root(client):
    res = client.get(reverse('api-root'))
    assert res.status_code == HTTPStatus.OK
    assert 'auth' in res.json()
