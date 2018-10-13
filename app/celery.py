import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

# celery starts with results_backend disabled without this...
app = Celery("app", broker="redis://localhost:6379", backend="redis://localhost:6379")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
