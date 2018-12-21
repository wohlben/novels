"""Conditionally creates pending fetches for new monitored novels ."""
from scrapes.models import Scrapes
from novels.models import Fiction
from . import PARSERS
import logging

__all__ = ["pending_fetches", "missing_novels", "add_queue_events"]

logger = logging.getLogger("scrapes.tasks")

PARSER_TYPE = "rrl novel"


def pending_fetches(*args):
    """Return Scrape urls of parser_type_id."""
    return Scrapes.objects.filter(
        parser_type_id=PARSERS[PARSER_TYPE], content=None
    ).values("url")


def missing_novels(*args):
    """Return monitored Fiction objects that should to be fetched."""
    return (
        Fiction.objects.exclude(watching=None)
        .exclude(url__in=pending_fetches())
        .filter(author=None)
    )


def refetch_novel(url):
    if url in pending_fetches():
        return False
    else:
        Scrapes.objects.create(url=url, parser_type_id=PARSERS[PARSER_TYPE])
        return True


def add_queue_events(*args):
    """Conditionally add a new pending fetch."""
    try:
        for novel in missing_novels():
            logger.info(f"adding '{novel.title}' to the pending fetches")
            Scrapes.objects.create(url=novel.url, parser_type_id=PARSERS[PARSER_TYPE])

        return True
    except Exception:  # pragma: no cover
        logger.exception(f"failed to add {novel.title} to scraping queue")
