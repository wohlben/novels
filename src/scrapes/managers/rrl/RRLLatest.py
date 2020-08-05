from scrapes.managers.ScrapeManagerBase import ScrapeManagerBase as _ScrapeManagerBase

from lxml import html as _html
from scrapes.models import ParseLog as _ParseLog, Parser as _Parser, Scrapes as _Scrapes
from novels.models import Fiction as _Fiction, Chapter as _Chapter
from django.utils import timezone as _timezone
from datetime import timedelta as _timedelta

__all__ = ["RRLLatestScraper"]


class RRLLatestScraper(_ScrapeManagerBase):
    parser_name = "rrl latest"

    BASE_URL = "https://www.royalroad.com"

    def parse(self):
        return self._latest_extractor()

    def _pending_fetches(self):
        """Return quantity of pending fetches relating to this module."""
        return _Scrapes.objects.filter(http_code=None, content=None, parser_type_id=self.get_parser_id()).count()

    def _last_fetch(self):
        """Return the last fetch object for modifications."""
        return _Scrapes.objects.filter(parser_type_id=self.get_parser_id()).last()

    def add_queue_event(self):
        """Conditionally add a new pending fetch."""
        try:
            pending_scrapes = self._pending_fetches()

            if pending_scrapes > 0:
                self.logger.warning(f'found {pending_scrapes} pending scrapes for "rrl latest" -- skipping queue')
                return False

            last_scrape = self._last_fetch()

            if last_scrape and last_scrape.last_change > _timezone.now() - _timedelta(minutes=15):
                self.logger.warning(f"last scrape was within 15 minutes ({last_scrape.last_change}) -- skipping queue")
                return False

            self.logger.info('adding new "rrl latest" to the scrape queue')

            _Scrapes.objects.create(
                url="https://www.royalroad.com/fictions/latest-updates", parser_type_id=self.get_parser_id(),
            )
            return True
        except Exception:  # pragma: no cover
            self.logger.exception('failed to add a new "rrl latest" scrape')

    def _latest_extractor(self):
        """Return False if no Parses were necessary, True the parsing was successful."""
        pending_parses = self.all_pending_parses()

        if pending_parses.count() == 0:
            self.logger.info("no rrl latest page to parse")
            return False

        self.logger.info(f"found {pending_parses.count()} scrapes to parse!")

        for scrape in pending_parses:
            self.logger.info(f"parsing {scrape.id}")

            tree = _html.fromstring(scrape.content)

            parse_log = _ParseLog.objects.create(scrape=scrape, parser_id=self.get_parser_id(), started=_timezone.now())

            novels = self._parse_fictions(tree)

            for novel, html_element in novels:
                self._parse_chapters(html_element, novel)

            parse_log.finished = _timezone.now()
            parse_log.success = True
            parse_log.save()

        return True

    def _parse_chapters(self, element, fiction):
        added_chapters = 0
        updated_chapters = 0
        chapters = element.xpath('.//li[@class="list-item"]')
        for element in chapters:
            try:
                chapter = dict()
                path = element.xpath("./a/@href")[0]
                chapter["url"] = f"{self.BASE_URL}{path}"
                chapter["remote_id"] = int(path.split("/")[5])
                chapter["title"] = element.xpath("./a/span/text()")[0]
                published_relative = element.xpath(".//time/text()")[0]
                chap, created = _Chapter.objects.get_or_create(
                    remote_id=chapter["remote_id"],
                    fiction=fiction,
                    defaults={**chapter, "published_relative": published_relative},
                )
                if created:
                    added_chapters += 1
                else:
                    updated_chapters += 1
                    _Chapter.objects.filter(id=chap.id).update(**chapter)

            except Exception:  # pragma: no cover
                self.logger.exception(f"failed to parse a chapter in {fiction}")
        if added_chapters + updated_chapters == len(chapters):
            self.logger.info(f"added {added_chapters} and updated {updated_chapters} for {fiction.title}")
        else:  # pragma: no cover
            self.logger.warning(
                f"expected {len(chapters)}, but only got {added_chapters} adds and {updated_chapters} updates for {fiction.title}"
            )
        return True

    def _parse_fictions(self, tree):
        created_fictions = 0
        updated_fictions = 0
        fictions = tree.xpath('//div[@class="fiction-list-item row"]')
        expected_fictions = len(fictions)
        # reverse fictions so that the discovered timestamp is from oldest to newest
        for element in reversed(fictions):
            try:
                fiction = {}
                fiction["pic_url"] = element.xpath("./figure//img/@src")[0]
                fiction["title"] = element.xpath('.//h2[@class="fiction-title"]/a/text()')[0]
                path = element.xpath('.//h2[@class="fiction-title"]/a/@href')[0]
                fiction["url"] = f"{self.BASE_URL}{path}"
                fiction_remote_id = int(path.split("/")[2])
                fic, created = _Fiction.objects.get_or_create(
                    source=_Parser.objects.get(name="rrl novel"), remote_id=fiction_remote_id, defaults=fiction,
                )
                if created:
                    created_fictions += 1
                else:
                    updated_fictions += 1
                    _Fiction.objects.filter(id=fic.id).update(**fiction)

                yield (fic, element)
            except Exception:  # pragma: no cover
                self.logger.exception("failed to parse a novel")
        if created_fictions + updated_fictions == expected_fictions:
            self.logger.info(f"added {created_fictions} and updated {updated_fictions}")
        else:
            self.logger.warning(
                f"expected {expected_fictions}, but only got {created_fictions} adds and {updated_fictions} updates parsing latest"
            )
