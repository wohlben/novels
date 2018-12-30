from . import ScrapeManagerBase

from scrapes.models import Scrapes as _Scrapes, ParseLog as _ParseLog
from novels.models import Chapter as _Chapter, Fiction as _Fiction
from datetime import timedelta as _timedelta, datetime as _datetime
from django.utils import timezone as _timezone
from django.db.models import Subquery as _Subquery

from lxml import html as _html
import re as _re
from lxml.etree import tostring as _tostring


class RRLChapterScraper(ScrapeManagerBase):
    parser_name = "rrl chapter"

    def parse(self, **kwargs):
        if kwargs.get("scrape_id"):
            return self._parse_chapter_scrape(kwargs["scrape_id"])

        return self.chapter_extractor()

    def chapter_extractor(self) -> bool:
        """Return False if no Parses were necessary. True if the parsind was successful."""
        pending_parses = self.all_pending_parses().values("id")

        if pending_parses.count() == 0:
            self.logger.info("no rrl chapter page to parse")
            return False

        self.logger.info(f"found {pending_parses.count()} chapter scrapes to parse!")

        for scrape in pending_parses:
            self.logger.info(f"parsing {scrape['id']}")
            self._parse_chapter_scrape(scrape["id"])

        return True

    def fetch_chapter(self, chapter_id: int, fetch_reason=None) -> int:
        chapter = _Chapter.objects.get(id=chapter_id)
        scrapes = _Scrapes.objects.filter(url=chapter.url)
        if scrapes.count() >= 1:
            scrape = scrapes.last()
        else:
            scrape = _Scrapes.objects.create(
                url=chapter.url,
                added_reason=fetch_reason,
                parser_type_id=self.get_parser_id(),
            )
        if scrape.http_code is None:
            return self._fetch_from_source(scrape.id)
        return scrape.id

    def pending_fetches(self):
        """Return Query Set of Scrapes within the last day."""
        return _Scrapes.objects.filter(
            parser_type_id=self.get_parser_id(),
            last_change__gt=_timezone.now() - _timedelta(days=1),
        ).values("url")

    def refetch_chapter(self, chapter_id):
        chapter = _Chapter.objects.get(id=chapter_id)
        if self.pending_fetches().count() > 0:
            self.logger.info(f"{chapter.title} is already queued, skipping")
            return False
        else:
            _Scrapes.objects.create(
                url=chapter.url, parser_type_id=self.get_parser_id()
            )
            self.logger.info(f"added {chapter.title} to the queue")
            return True

    def add_queue_events(self):
        """Conditionally add a new pending fetch."""
        try:
            pending_chapters = self._missing_chapters()
            pending_chapters.select_related("fiction__monitored", "fiction__title")

            for chapter in pending_chapters:
                self.logger.info(
                    f"adding '{chapter.title}' chapter from '{chapter.fiction.title}' to the pending fetches"
                )
                _Scrapes.objects.create(
                    url=chapter.url, parser_type_id=self.get_parser_id()
                )

            return True
        except Exception:  # pragma: no cover
            self.logger.exception('failed to add a new "rrl chapter" scrape')

    @staticmethod
    def _monitored_novels():
        """Return IDs of all monitored Fiction objects."""
        return _Fiction.objects.exclude(watching=None)

    def _missing_chapters(self):
        """Return all chapters of monitored novels without content."""
        return _Chapter.objects.filter(
            content=None, fiction__in=_Subquery(self._monitored_novels().values("id"))
        ).exclude(url__in=_Subquery(self.pending_fetches().values("url")))

    # PARSER #

    def _parse_chapter_scrape(self, scrape_id: int) -> bool:
        scrape = _Scrapes.objects.get(id=scrape_id)
        chapter = _Chapter.objects.get(url=scrape.url)  # TODO: get or create
        parse_log = _ParseLog.objects.create(
            scrape=scrape,
            parser_id=self.get_parser_id(),
            started=_timezone.now(),
            modified_object={
                "count": 1,
                "chapters": [chapter.id],
                "types": ["chapters"],
            },
        )
        try:
            tree = _html.fromstring(scrape.content)

            chapter_content = ""
            for i in tree.cssselect(".chapter-content"):
                chapter_content += self._clean_chapter_content(_tostring(i))
            chapter.content = chapter_content

            remote_id = scrape.url.split("/")[-2]
            if chapter.remote_id is None:
                chapter.remote_id = remote_id
            if chapter.remote_id != remote_id:
                self.logger.error(
                    "unexpected remote_id. not updating content on possible parsing error!"
                )
                raise Exception("unexpected Data")

            timestamp = int(tree.xpath('//i[@title="Published"]/../time/@unixtime')[0])
            chapter.published = _timezone.make_aware(
                _datetime.utcfromtimestamp(timestamp), _timezone.utc
            )

            fiction_remote_id = int(scrape.url.split("/")[4])
            fiction = _Fiction.objects.get(remote_id=fiction_remote_id)

            chapter.fiction = fiction
            chapter.save()

            self.logger.info(
                f'updated content of "{chapter.fiction.title}: {chapter.title}"'
            )

            parse_log.finished = _timezone.now()
            parse_log.success = True
            parse_log.save()
        except Exception:  # pragma: no cover
            self.logger.exception(f"failed to parse chapter from {scrape.url}")
            parse_log.success = False
            parse_log.save()
            return False

    @staticmethod
    def _clean_chapter_content(content):
        content = (
            content.decode("unicode_escape")
            .encode("raw_unicode_escape")
            .decode("utf-8")
        )
        removed_scripts = _re.sub(r"<script.*?</script>", "", str(content))
        return removed_scripts
