from celery import shared_task as _shared_task
import logging as _logging
from novels.models import Chapter as _Chapter
from novels.processing import TextRanker

_logger = _logging.getLogger("novels.tasks")

ranker = TextRanker()


@_shared_task
def highlight_extractor_task():
    _logger.info("starting periodic highlight extraction")
    chapters = (
        _Chapter.objects.exclude(content=None).filter(highlight=None).values("id")[:50]
    )
    for chapter in chapters:
        ranker.extract_highlights(chapter["id"])
    _logger.info(f"finished extracting highlights from {len(chapters)} chapters")
    return True


@_shared_task
def character_extractor_task():
    _logger.info("starting periodic character extraction")
    chapters = (
        _Chapter.objects.exclude(content=None).filter(characters=None).values("id")[:50]
    )
    for chapter in chapters:
        ranker.extract_characters(chapter["id"])
    _logger.info(f"finished extracting characters from {len(chapters)} chapters")
