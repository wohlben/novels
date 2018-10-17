"""discovery for pending rrl latest parses and parsing them into fictions and novels."""
from lxml import html
from scrapes.models import ParseLog
from novels.models import Fiction, Chapter
import logging
from django.utils import timezone
from . import all_pending_parses

__all__ = ['latest_extractor']

logger = logging.getLogger("scrapes.tasks")
BASE_URL = "https://www.royalroad.com"


def latest_extractor(parser_id):
    """Return False if no Parses were necessary, True the parsing was successful."""
    pending_parses = all_pending_parses(parser_id)

    if pending_parses.count() == 0:
        logger.info("nothing to parse")
        return False

    logger.info(f"found {pending_parses.count()} scrapes to parse!")

    for scrape in pending_parses:
        logger.info(f"parsing {scrape.id}")

        tree = html.fromstring(scrape.content)

        parse_log = ParseLog.objects.create(
            scrape=scrape, parser_id=parser_id, started=timezone.now()
        )

        novels = _parse_fictions(tree)

        for novel, html_element in novels:
            _parse_chapters(html_element, novel)

    parse_log.finished = timezone.now()
    parse_log.success = True
    parse_log.save()

    return True


def _parse_chapters(element, fiction):
    for element in element.xpath('.//li[@class="list-item"]'):
        try:
            chapter = {}
            chapter["fiction"] = fiction
            path = element.xpath("./a/@href")[0]
            chapter["url"] = f"{BASE_URL}{path}"
            chapter["remote_id"] = int(path.split("/")[5])
            chapter["title"] = element.xpath("./a/span/text()")[0]
            published_relative = element.xpath(".//time/text()")[0]
            chap, created = Chapter.objects.get_or_create(
                remote_id=chapter["remote_id"],
                defaults={**chapter, "published_relative": published_relative},
            )
            if created:
                logger.info(f'created "{fiction.title}": "{chap.title}"')
            else:
                Chapter.objects.filter(id=chap.id).update(**chapter)
                logger.info(f'refreshed "{fiction.title}": "{chap.title}"')

        except Exception:  # pragma: no cover
            logger.exception(f"failed to parse a chapter in {fiction}")
    return True


def _parse_fictions(tree):
    for element in tree.xpath('//div[@class="fiction-list-item row"]'):
        try:
            fiction = {}
            fiction["pic_url"] = element.xpath("./figure/img/@src")[0]
            fiction["title"] = element.xpath('.//h2[@class="fiction-title"]/a/text()')[
                0
            ]
            path = element.xpath('.//h2[@class="fiction-title"]/a/@href')[0]
            fiction["url"] = f"{BASE_URL}{path}"
            fiction["remote_id"] = int(path.split("/")[2])
            fic, created = Fiction.objects.get_or_create(
                remote_id=fiction["remote_id"], defaults=fiction
            )
            if created:
                logger.info(f'created "{fic.title}"')
            elif fic.monitored is False:
                logger.info(f'skipping "{fic.title}" as its not monitored')
                continue
            else:
                Fiction.objects.filter(id=fic.id).update(**fiction)
                logger.info(f'refreshed "{fic.title}"')

            yield (fic, element)
        except Exception:  # pragma: no cover
            logger.exception("failed to parse a novel")
