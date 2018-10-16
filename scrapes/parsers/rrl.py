"""discovery for pending rrl latest parses and parsing them into fictions and novels."""
from lxml import html
from scrapes.models import Scrapes, ParseLog
from novels.models import Fiction, Chapter
import logging
from django.utils import timezone
from datetime import datetime
import re
from html import unescape
import tomd
from lxml.etree import tostring


logger = logging.getLogger("scrapes.tasks")
BASE_URL = "https://www.royalroad.com"


def _available_chapter_urls(novel_ids):
    return Chapter.objects.filter(fiction_id__in=novel_ids).values('url')


def all_pending_parses(parser_id):
    """Return the pending parses that this parser can handle."""
    return Scrapes.objects.filter(http_code=200, parser_type_id=parser_id, parselog__isnull=True)


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

def novel_extractor(parser_id):
    """Return False if no Parses were necessary. True if the parsind was successful."""
    pending_parses = all_pending_parses(parser_id)

    if pending_parses.count() == 0:
        logger.info("nothing to parse")
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
            success_monitor = False
        parse_log.save()
    return success_monitor




def chapter_extractor(parser_id):
    """Return False if no Parses were necessary. True if the parsind was successful."""
    pending_parses = all_pending_parses(parser_id)

    if pending_parses.count() == 0:
        logger.info("nothing to parse")
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
            success_monitor = False
        parse_log.save()

    return True


def _clean_chapter_content(content):
    removedScripts = re.sub(r"<script.*?</script>", "", str(content))
    removeHtmlEscapes = unescape(removedScripts)
    content = tomd.convert(removeHtmlEscapes.replace("<br/>", "\n"))
    return content


def _parse_chapter_page(element, url):
    try:
        remote_id = url.split('/')[-2]
        chap, created = Chapter.objects.get_or_create(url=url)
        chap.content = _clean_chapter_content(tostring(element.cssselect('.chapter-content')[0]))
        if chap.remote_id is None:
            chap.remote_id = remote_id
        if chap.remote_id != remote_id:
            logger.error('unexpected remote_id. not updating content on possible parsing error!')
            return False
        timestamp = int(element.xpath('//i[@title="Published"]/../time/@unixtime')[0])
        chap.published = timezone.make_aware(datetime.utcfromtimestamp(timestamp), timezone.utc)
        chap.save()
        logging.info(f'updated content of "{chap.title}"')
        return True
    except Exception:  # pragma: no cover
        logging.exception("failed to parse chapter")


def _parse_fiction_page(element, url):
    try:
        remote_id = url.split('/')[-2]
        fic, created = Fiction.objects.get_or_create(url=url)
        if fic.remote_id is None:
            fic.remote_id = remote_id
        if fic.remote_id != remote_id:
            logger.error('unexpected remote_id. not updating content on possible parsing error!')
            return False

        chapters = element.xpath('//tr')
        for chapter in chapters:
            url_element = chapter.xpath('./td/a/@href')
            if len(url_element) == 0:
                continue
            chap_url = BASE_URL + chapter.xpath('./td/a/@href')[0]
            chap_remote_id = chap_url.split('/')[-2]
            chap, created = Chapter.objects.get_or_create(url=chap_url, fiction=fic, defaults={'remote_id': chap_remote_id})
            chap.title = chapter.xpath('./td/a/text()')[0].encode('utf-8').decode('unicode_escape').strip()
            chap.save()
            logger.info(f'created chapter ')

        fic.author = element.xpath('//h4[@property="author"]//a/text()')[0]
        fic.save()
        logger.info(f'updated content of "{fic.title}"')
        return True
    except Exception:  # pragma: no cover
        logging.exception("failed to parse chapter")

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
