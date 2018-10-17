"""discovery for pending rrl latest parses and parsing them into fictions and novels."""
from lxml import html
from scrapes.models import ParseLog
from . import all_pending_parses
from novels.models import Chapter
import logging
from django.utils import timezone
from datetime import datetime
import re
from html import unescape
import tomd
from lxml.etree import tostring

__all__ = ["chapter_extractor"]

logger = logging.getLogger("scrapes.tasks")
BASE_URL = "https://www.royalroad.com"


def chapter_extractor(parser_id):
    """Return False if no Parses were necessary. True if the parsind was successful."""
    pending_parses = all_pending_parses(parser_id)

    if pending_parses.count() == 0:
        logger.info("no rrl chapter page to parse")
        return False

    logger.info(f"found {pending_parses.count()} chapter scrapes to parse!")

    success_monitor = True

    for scrape in pending_parses:
        logger.info(f"parsing {scrape.id}")

        tree = html.fromstring(scrape.content)

        parse_log = ParseLog.objects.create(
            scrape=scrape, parser_id=parser_id, started=timezone.now()
        )

        data_extracted = _parse_chapter_page(tree, scrape.url)
        parse_log.finished = timezone.now()
        if data_extracted:
            parse_log.success = success_monitor
        else:
            success_monitor = False  # pragma: no cover
        parse_log.save()

    return True


def _clean_chapter_content(content):
    content = content.decode("unicode_escape").strip()
    removedScripts = re.sub(r"<script.*?</script>", "", str(content))
    removeHtmlEscapes = unescape(removedScripts)
    content = tomd.convert(removeHtmlEscapes.replace("<br/>", "\n"))
    return content


def _parse_chapter_page(element, url):
    try:
        remote_id = url.split("/")[-2]
        chap = Chapter.objects.get(url=url)
        chap.content = _clean_chapter_content(
            tostring(element.cssselect(".chapter-content")[0])
        )
        if chap.remote_id is None:
            chap.remote_id = remote_id  # pragma: no cover
        if chap.remote_id != remote_id:  # pragma: no cover
            logger.error(
                "unexpected remote_id. not updating content on possible parsing error!"
            )
            return False
        timestamp = int(element.xpath('//i[@title="Published"]/../time/@unixtime')[0])
        chap.published = timezone.make_aware(
            datetime.utcfromtimestamp(timestamp), timezone.utc
        )
        chap.save()
        logging.info(f'updated content of "{chap.title}"')
        return True
    except Exception:  # pragma: no cover
        logging.exception(f"failed to parse chapter from {url}")
