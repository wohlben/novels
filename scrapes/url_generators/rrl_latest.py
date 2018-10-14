from scrapes.models import Scrapes, Parser
from datetime import timedelta
from django.utils import timezone
import logging

logger = logging.getLogger("scrapes.tasks")


def all_pending_fetches(parser_type_id):
    return Scrapes.objects.filter(
        http_code=None, content=None, parser_type_id=parser_type_id
    ).count()


def last_fetch(parser_type_id):
    return Scrapes.objects.filter(parser_type_id=parser_type_id).last()


def add_queue_event(parser_type_id):
    try:
        pending_scrapes = all_pending_fetches(parser_type_id)

        if pending_scrapes > 0:
            logger.warning(
                f'found {pending_scrapes} pending scrapes for "rrl latest" -- skipping queue'
            )
            return False

        last_scrape = last_fetch(parser_type_id)

        if last_scrape and last_scrape.last_change > timezone.now() - timedelta(minutes=15):
            logger.warning(
                f"last scrape was within 15 minutes ({last_scrape.last_change}) -- skipping queue"
            )
            return False

        logger.info('adding new "rrl latest" to the scrape queue')

        Scrapes.objects.create(
            url="https://www.royalroad.com/fictions/latest-updates",
            parser_type_id=parser_type_id,
        )
        return True
    except Exception as e: # pragma: no cover
        logger.error('failed to add a new "rrl latest" scrape')
        raise e
