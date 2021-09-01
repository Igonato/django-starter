"""Run Celery with autoreload for development"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import autoreload


def tasks_watchdog(sender, **kwargs):
    sender.watch_dir(settings.BASE_DIR, '**/*tasks.py')


def restart_celery():
    if os.name == 'nt':
        os.system('taskkill /im celery.exe /f')
    else:
        os.system('pkill celery')
    os.system('celery -A config worker -c 1 -l INFO')


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Starting celery worker with autoreload...')
        autoreload.autoreload_started.connect(tasks_watchdog)
        autoreload.run_with_reloader(restart_celery)
