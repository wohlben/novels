"""Provides discovery of pending fetches and creates them conditionally."""
from scrapes.models import Scrapes
from datetime import timedelta
from django.utils import timezone
import logging
from . import PARSERS

logger = logging.getLogger("scrapes.tasks")

__all__ = ["pending_fetches", "last_fetch", "add_queue_event"]

PARSER_TYPE = "rrl latest"


def pending_fetches(*args):
    """Return quantity of pending fetches relating to this module."""
    return Scrapes.objects.filter(
        http_code=None, content=None, parser_type_id=PARSERS[PARSER_TYPE]
    ).count()


def last_fetch(*args):
    """Return the last fetch object for modifications."""
    return Scrapes.objects.filter(parser_type_id=PARSERS[PARSER_TYPE]).last()


def add_queue_event(*args):
    """Conditionally add a new pending fetch."""
    try:
        pending_scrapes = pending_fetches()

        if pending_scrapes > 0:
            logger.warning(
                f'found {pending_scrapes} pending scrapes for "rrl latest" -- skipping queue'
            )
            return False

        last_scrape = last_fetch()

        if last_scrape and last_scrape.last_change > timezone.now() - timedelta(
            minutes=15
        ):
            logger.warning(
                f"last scrape was within 15 minutes ({last_scrape.last_change}) -- skipping queue"
            )
            return False

        logger.info('adding new "rrl latest" to the scrape queue')

        Scrapes.objects.create(
            url="https://www.royalroad.com/fictions/latest-updates",
            parser_type_id=PARSERS[PARSER_TYPE],
        )
        return True
    except Exception:  # pragma: no cover
        logger.exception('failed to add a new "rrl latest" scrape')
