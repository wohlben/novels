"""Conditionally creates pending fetches for new monitored novels ."""
from scrapes.models import Scrapes
from novels.models import Chapter, Fiction
import logging

__all__ = ["pending_fetches", "missing_novels", "add_queue_events"]

logger = logging.getLogger("scrapes.tasks")


def pending_fetches(parser_type_id):
    """Return Scrape urls of parser_type_id."""
    return Scrapes.objects.filter(parser_type_id=parser_type_id, content=None).values("url")


def missing_novels(parser_type_id):
    """Return monitored Fiction objects that should to be fetched."""
    return Fiction.objects.exclude(watching=None).exclude(
        url__in=pending_fetches(parser_type_id)).filter(author=None
    )


def add_queue_events(parser_type_id):
    """Conditionally add a new pending fetch."""
    try:
        for novel in missing_novels(parser_type_id):
            logger.info(f"adding '{novel.title}' to the pending fetches")
            Scrapes.objects.create(url=novel.url, parser_type_id=parser_type_id)

        return True
    except Exception:  # pragma: no cover
        logger.exception('failed to add a new "rrl latest" scrape')
