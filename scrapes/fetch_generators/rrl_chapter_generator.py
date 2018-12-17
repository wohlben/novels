"""Conditionally creates pending fetches for unparsed chapters ."""
from scrapes.models import Scrapes
from novels.models import Chapter, Fiction
from datetime import timedelta
from django.utils import timezone
import logging

__all__ = [
    "pending_fetches",
    "missing_chapters",
    "monitored_novels",
    "add_queue_events",
]

logger = logging.getLogger("scrapes.tasks")


def pending_fetches(parser_type_id):
    """Return Query Set of Scrapes within the last day."""
    return Scrapes.objects.filter(
        parser_type_id=parser_type_id,
        last_change__gt=timezone.now() - timedelta(days=1),
    ).values("url")


def missing_chapters(parser_type_id):
    """Return all chapters of monitored novels without content."""
    return Chapter.objects.filter(
        content=None, fiction__in=monitored_novels(parser_type_id)
    ).exclude(url__in=pending_fetches(parser_type_id))


def monitored_novels(parser_type_id):
    """Return IDs of all monitored Fiction objects."""
    return Fiction.objects.exclude(watching=None).values("id")


def add_queue_events(parser_type_id):
    """Conditionally add a new pending fetch."""
    try:
        pending_chapters = missing_chapters(parser_type_id)
        pending_chapters.select_related("fiction__monitored", "fiction__title")

        for chapter in pending_chapters:
            logger.info(
                f"adding '{chapter.title}' chapter from '{chapter.fiction.title}' to the pending fetches"
            )
            Scrapes.objects.create(url=chapter.url, parser_type_id=parser_type_id)

        return True
    except Exception:  # pragma: no cover
        logger.exception('failed to add a new "rrl latest" scrape')
