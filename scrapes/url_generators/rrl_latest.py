from scrapes.models import Scrapes, Parser
from datetime import timedelta
from django.utils import timezone
import logging

logger = logging.getLogger("scrapes.tasks")


def add_queue_event(parser_type_id):
    try:
        pending_scrapes = Scrapes.objects.filter(
            http_code=None, content=None, parser_type_id=parser_type_id
        ).count()

        if pending_scrapes > 0:
            logger.warning(
                f'found {pending_scrapes} pending scrapes for "rrl latest" -- skipping queue'
            )
            return False

        last_scrape = Scrapes.objects.filter(parser_type_id=parser_type_id).last()

        if last_scrape.last_change > timezone.now() - timedelta(minutes=15):
            logger.warning(
                f"last scrape was within 15 minutes ({last_scrape.last_change}) -- skipping queue"
            )
            return False

        logger.info('adding new "rrl latest" to the scrape queue')

        new_scrape = Scrapes.objects.create(
            url="https://www.royalroad.com/fictions/latest-updates",
            parser_type_id=parser_type_id,
        )
        return True
    except Exception as e:
        logger.error('failed to add a new "rrl latest" scrape')
        raise e
