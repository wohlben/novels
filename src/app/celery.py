import os
from celery import Celery
from . import env_variable

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

# celery starts with results_backend disabled without this...
app = Celery(
    "app",
    broker=env_variable("cache", "redis://cache:6379") + "/1",
    backend=env_variable("results", "django-db"),
)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
