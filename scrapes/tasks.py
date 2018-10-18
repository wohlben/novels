from celery import shared_task
from requests import get
from scrapes.fetch_generators import (
    rrl_latest_generator,
    rrl_chapter_generator,
    rrl_novel_generator,
)
from scrapes.parsers import rrl_chapter_parser, rrl_novel_parser, rrl_latest_parser
import logging
from scrapes.models import Scrapes, Parser

logger = logging.getLogger("scrapes.tasks")

rrl_latest_parser_id = Parser.objects.get(name="rrl latest").id
rrl_chapter_parser_id = Parser.objects.get(name="rrl chapter").id
rrl_novel_parser_id = Parser.objects.get(name="rrl novel").id


@shared_task
def fetch_content():  # TODO: mock response..... #TODO: dont fetch if another Scrape < 15 min was done to the same url
    """Fetch an URL from a remote server."""
    try:
        instance = Scrapes.objects.filter(http_code=None, content=None).first()
        if not instance:
            logger.info("no pending scrapes")
            return True

        logger.info(f"fetching {instance.url} for {instance.id}")

        with get(instance.url) as page:
            instance.content = page.content
            instance.http_code = page.status_code
            instance.save()

            logger.info(f"finished {instance.id} with https_code {instance.http_code}")

        return True
    except Exception:
        logger.exception(f"failed to fetch content for {instance.url}")


@shared_task
def generators():
    """Periodic task to conditionally enqueue new fetches."""
    rrl_latest_generator.add_queue_event(rrl_latest_parser_id)
    rrl_chapter_generator.add_queue_events(rrl_chapter_parser_id)
    rrl_novel_generator.add_queue_events(rrl_novel_parser_id)
    return True


@shared_task
def parsers():
    """Periodic task to parse all available rrl fetches."""
    rrl_latest_parser.latest_extractor(rrl_latest_parser_id)
    rrl_chapter_parser.chapter_extractor(rrl_chapter_parser_id)
    rrl_novel_parser.novel_extractor(rrl_novel_parser_id)
    return True
