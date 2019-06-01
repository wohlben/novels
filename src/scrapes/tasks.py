from celery import shared_task
from requests import get
from scrapes.managers import Managers
from scrapes.models import Scrapes
import logging

logger = logging.getLogger("scrapes.tasks")

managers = Managers()


@shared_task
def fetch_content(
    scrape_id=None
):  # TODO: mock response..... # TODO: dont fetch if another Scrape < 15 min was done to the same url
    """Fetch an URL from a remote server."""
    try:
        if scrape_id is None:
            instance = managers.manager.scrape_queue().first()
        else:
            instance = Scrapes.objects.get(id=scrape_id)
        if not instance:
            logger.info("no pending scrapes")
            return True

        logger.info(f"fetching {instance.url} for {instance.id}")

        with get(instance.url) as page:
            instance.content = page.text
            instance.http_code = page.status_code
            instance.save()

            logger.info(f"finished {instance.id} with https_code {instance.http_code}")

        try:
            getattr(managers, instance.parser_type.name.replace(" ", "_")).parse()
        except Exception:
            logger.error(f"couldn't trigger the parse for {instance.parser_type.name}")
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
    managers.rrl_latest.parse()
    managers.rrl_novel.parse()
    managers.rrl_chapter.parse()
    return True
