from celery import shared_task
from requests import get
from scrapes import fetch_generators, parsers
import logging

logger = logging.getLogger("scrapes.tasks")


@shared_task
def fetch_content():  # TODO: mock response..... # TODO: dont fetch if another Scrape < 15 min was done to the same url
    """Fetch an URL from a remote server."""
    try:
        instance = fetch_generators.scrape_queue().first()
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
def generators_task():
    fetch_generators.rrl_latest_generator.add_queue_event()
    fetch_generators.rrl_novel_generator.add_queue_events()
    fetch_generators.rrl_chapter_generator.add_queue_events()
    return True


@shared_task
def parsers_task():
    """Periodic task to parse all available rrl fetches."""
    parsers.rrl_latest_parser.latest_extractor()
    parsers.rrl_chapter_parser.chapter_extractor()
    parsers.rrl_novel_parser.novel_extractor()
    return True
