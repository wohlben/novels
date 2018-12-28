"""discovery for pending rrl latest parses and parsing them into fictions and novels."""
from lxml import html
from scrapes.models import ParseLog, Scrapes
from novels.models import Chapter, Fiction
from django.utils import timezone
from datetime import datetime
import re
from lxml.etree import tostring


class RRLChapterParserMixin(object):
    def parse(self):
        return self.chapter_extractor()

    def chapter_extractor(self):
        """Return False if no Parses were necessary. True if the parsind was successful."""
        pending_parses = self.all_pending_parses().values("id")

        if pending_parses.count() == 0:
            self.logger.info("no rrl chapter page to parse")
            return False

        self.logger.info(f"found {pending_parses.count()} chapter scrapes to parse!")

        for scrape in pending_parses:
            self.logger.info(f"parsing {scrape['id']}")
            self.parse_chapter_scrape(scrape["id"])

        return True

    @staticmethod
    def _clean_chapter_content(content):
        content = (
            content.decode("unicode_escape")
            .encode("raw_unicode_escape")
            .decode("utf-8")
        )
        removed_scripts = re.sub(r"<script.*?</script>", "", str(content))
        return removed_scripts

    def parse_chapter_scrape(self, scrape_id: int) -> bool:
        scrape = Scrapes.objects.get(id=scrape_id)
        chapter = Chapter.objects.get(url=scrape.url)  # TODO: get or create
        parse_log = ParseLog.objects.create(
            scrape=scrape,
            parser_id=self.get_parser_id(),
            started=timezone.now(),
            modified_object={
                "count": 1,
                "chapters": [chapter.id],
                "types": ["chapters"],
            },
        )
        try:
            tree = html.fromstring(scrape.content)

            chapter_content = ""
            for i in tree.cssselect(".chapter-content > *"):
                chapter_content += self._clean_chapter_content(tostring(i))
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
            chapter.published = timezone.make_aware(
                datetime.utcfromtimestamp(timestamp), timezone.utc
            )

            fiction_remote_id = int(scrape.url.split("/")[4])
            fiction = Fiction.objects.get(remote_id=fiction_remote_id)

            chapter.fiction = fiction
            chapter.save()

            self.logger.info(
                f'updated content of "{chapter.fiction.title}: {chapter.title}"'
            )

            parse_log.finished = timezone.now()
            parse_log.success = True
            parse_log.save()
        except Exception:  # pragma: no cover
            self.logger.exception(f"failed to parse chapter from {scrape.url}")
            parse_log.success = False
            parse_log.save()
            return False
