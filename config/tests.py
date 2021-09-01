from .celery import debug_task


def test_celery_task(celery_worker):
    assert debug_task.delay().get(timeout=5) is None
