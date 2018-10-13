from celery import shared_task
from requests import get
from scrapes.url_generators import rrl_latest as rrl_latest_generator
from scrapes.parsers import rrl as rrl_latest_parser
import logging
from scrapes.models import Scrapes, Parser

logger = logging.getLogger("scrapes.tasks")

rrl_latest_parser_id = Parser.objects.get(name="rrl latest").id
rrl_chapter_parser_id = Parser.objects.get(name="rrl chapter").id
rrl_novel_parser_id = Parser.objects.get(name="rrl novel").id


@shared_task
def fetch_content():
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
    except Exception as e:
        logger.error(f"failed to fetch content for {instance.url}")
        raise e


@shared_task
def fetch_latest():
    rrl_latest_generator.add_queue_event(rrl_latest_parser_id)


@shared_task
def parse_latest():
    rrl_latest_parser.latest_extractor(rrl_latest_parser_id)
