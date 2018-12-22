from celery import shared_task
from requests import get
from scrapes.managers import Managers
import logging

logger = logging.getLogger("scrapes.tasks")

managers = Managers()


@shared_task
def fetch_content():  # TODO: mock response..... # TODO: dont fetch if another Scrape < 15 min was done to the same url
    """Fetch an URL from a remote server."""
    try:
        instance = managers.manager.scrape_queue().first()
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
    managers.rrl_latest.add_queue_event()
    managers.rrl_novel.add_queue_events()
    managers.rrl_chapter.add_queue_events()
    return True


@shared_task
def parsers_task():
    """Periodic task to parse all available rrl fetches."""
    managers.rrl_latest.latest_extractor()
    managers.rrl_chapter.chapter_extractor()
    managers.rrl_novel.novel_extractor()
    return True
