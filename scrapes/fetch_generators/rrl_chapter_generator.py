"""Conditionally creates pending fetches for unparsed chapters ."""
from scrapes.models import Scrapes
from novels.models import Chapter, Fiction
from datetime import timedelta
from django.utils import timezone
from . import PARSERS
import logging

__all__ = [
    "pending_fetches",
    "missing_chapters",
    "monitored_novels",
    "add_queue_events",
    "refetch_chapter",
]

logger = logging.getLogger("scrapes.tasks")

PARSER_TYPE = "rrl chapter"


def pending_fetches(*args):
    """Return Query Set of Scrapes within the last day."""
    return Scrapes.objects.filter(
        parser_type_id=PARSERS[PARSER_TYPE],
        last_change__gt=timezone.now() - timedelta(days=1),
    ).values("url")


def missing_chapters(*args):
    """Return all chapters of monitored novels without content."""
    return Chapter.objects.filter(
        content=None, fiction__in=monitored_novels(PARSERS[PARSER_TYPE])
    ).exclude(url__in=pending_fetches())


def monitored_novels(*args):
    """Return IDs of all monitored Fiction objects."""
    return Fiction.objects.exclude(watching=None).values("id")


def refetch_chapter(chapter_id):
    chapter = Chapter.objects.get(id=chapter_id)
    if chapter.url in pending_fetches(PARSERS[PARSER_TYPE]):
        return False
    else:
        Scrapes.objects.create(url=chapter.url, parser_type_id=PARSERS[PARSER_TYPE])
        return True


def add_queue_events(*args):
    """Conditionally add a new pending fetch."""
    try:
        pending_chapters = missing_chapters(PARSERS[PARSER_TYPE])
        pending_chapters.select_related("fiction__monitored", "fiction__title")

        for chapter in pending_chapters:
            logger.info(
                f"adding '{chapter.title}' chapter from '{chapter.fiction.title}' to the pending fetches"
            )
            Scrapes.objects.create(url=chapter.url, parser_type_id=PARSERS[PARSER_TYPE])

        return True
    except Exception:  # pragma: no cover
        logger.exception('failed to add a new "rrl latest" scrape')
