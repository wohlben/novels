"""discovery for pending rrl latest parses and parsing them into fictions and novels."""
from lxml import html
from scrapes.models import ParseLog
from novels.models import Fiction, Chapter
import logging
from django.utils import timezone


class RRLNovelParserMixin(object):

    BASE_URL = "https://www.royalroad.com"
    def novel_extractor(self):
        """Return False if no Parses were necessary. True if the parsind was successful."""
        pending_parses = self.all_pending_parses()

        if pending_parses.count() == 0:
            self.logger.info("no rrl novel page to parse")
            return False

        self.logger.info(f"found {pending_parses.count()} chapter scrapes to parse!")

        success_monitor = True

        for scrape in pending_parses:
            self.logger.info(f"parsing {scrape.id}")

            tree = html.fromstring(scrape.content)

            parse_log = ParseLog.objects.create(
                scrape=scrape, parser_id=self.parser_id, started=timezone.now()
            )
            data_extracted = self._parse_fiction_page(tree, scrape.url)
            parse_log.finished = timezone.now()
            if data_extracted:
                parse_log.success = success_monitor
            else:
                success_monitor = False  # pragma: no cover
            parse_log.save()
        return success_monitor


    def _parse_fiction_page(self, element, url):
        try:
            remote_id = url.split("/")[-2]
            fic, created = Fiction.objects.get_or_create(url=url)
            if fic.remote_id is None:  # pragma: no cover
                fic.remote_id = remote_id
            if fic.remote_id != remote_id:  # pragma: no cover
                self.logger.error(
                    "unexpected remote_id. not updating content on possible parsing error!"
                )
                return False

            chapters = element.xpath("//tr")
            created_chapters = 0
            for chapter in chapters:
                url_element = chapter.xpath("./td/a/@href")
                if len(url_element) == 0:
                    continue
                chap_url = self.BASE_URL + chapter.xpath("./td/a/@href")[0]
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
            self.logger.info(f'updated content of "{fic.title}" and added {created_chapters}')
            return True
        except Exception:  # pragma: no cover
            logging.exception("failed to parse chapter")
