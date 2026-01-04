"""
Celery config for pdfactory project.

It exposes the Celery application as a module-level variable named ``application``.

For more information on this file, see
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html#using-celery-with-django
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

application = Celery("main")
application.config_from_object("django.conf:settings", namespace="CELERY")
application.autodiscover_tasks()
