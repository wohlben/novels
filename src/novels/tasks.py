from celery import shared_task as _shared_task
import logging as _logging
from novels.models import Chapter as _Chapter

_logger = _logging.getLogger("novels.tasks")


