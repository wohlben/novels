"""discovery for pending rrl latest parses and parsing them into fictions and novels."""
from lxml import html
from scrapes.models import ParseLog
from novels.models import Fiction, Chapter
import logging
from django.utils import timezone
from . import all_pending_parses

__all__ = ["novel_extractor"]

logger = logging.getLogger("scrapes.tasks")
BASE_URL = "https://www.royalroad.com"


def novel_extractor(parser_id):
    """Return False if no Parses were necessary. True if the parsind was successful."""
    pending_parses = all_pending_parses(parser_id)

    if pending_parses.count() == 0:
        logger.info("no rrl novel page to parse")
        return False

    logger.info(f"found {pending_parses.count()} chapter scrapes to parse!")

    success_monitor = True

    for scrape in pending_parses:
        logger.info(f"parsing {scrape.id}")

        tree = html.fromstring(scrape.content)

        parse_log = ParseLog.objects.create(
            scrape=scrape, parser_id=parser_id, started=timezone.now()
        )
        data_extracted = _parse_fiction_page(tree, scrape.url)
        parse_log.finished = timezone.now()
        if data_extracted:
            parse_log.success = success_monitor
        else:
            success_monitor = False  # pragma: no cover
        parse_log.save()
    return success_monitor


def _parse_fiction_page(element, url):
    try:
        remote_id = url.split("/")[-2]
        fic, created = Fiction.objects.get_or_create(url=url)
        if fic.remote_id is None:  # pragma: no cover
            fic.remote_id = remote_id
        if fic.remote_id != remote_id:  # pragma: no cover
            logger.error(
                "unexpected remote_id. not updating content on possible parsing error!"
            )
            return False

        chapters = element.xpath("//tr")
        created_chapters = 0
        for chapter in chapters:
            url_element = chapter.xpath("./td/a/@href")
            if len(url_element) == 0:
                continue
            chap_url = BASE_URL + chapter.xpath("./td/a/@href")[0]
            chap_remote_id = chap_url.split("/")[-2]
            chap, created = Chapter.objects.get_or_create(
                url=chap_url, fiction=fic, defaults={"remote_id": chap_remote_id}
            )
            chap.title = (
                chapter.xpath("./td/a/text()")[0]
                .encode("utf-8")
                .decode("unicode_escape")
                .strip()
            )
            chap.save()
            created_chapters += 1

        fic.author = element.xpath('//h4[@property="author"]//a/text()')[0]
        fic.save()
        logger.info(f'updated content of "{fic.title}" and added {created_chapters}')
        return True
    except Exception:  # pragma: no cover
        logging.exception("failed to parse chapter")
