from scrapes.managers.ScrapeManagerBase import ScrapeManagerBase as _ScrapeManagerBase
from scrapes.models import Scrapes as _Scrapes, ParseLog as _ParseLog
from django.db.models import Subquery as _Subquery
from lxml import html as _html
from novels.models import Fiction as _Fiction, Chapter as _Chapter
from django.utils import timezone as _timezone


__all__ = ["RRLNovelScraper"]


class RRLNovelScraper(_ScrapeManagerBase):
    BASE_URL = "https://www.royalroad.com"
    parser_name = "rrl novel"

    def parse(self):
        return self.novel_extractor()

    def pending_fetches(self):
        """Return Scrape urls of parser_type_id."""
        return _Scrapes.objects.filter(
            parser_type_id=self.get_parser_id(), content=None
        )

    def missing_novels(self, *args, **kwargs):
        """Return monitored Fiction objects that should to be fetched."""
        qs = (
            _Fiction.objects.exclude(watching=None)
            .exclude(url__in=_Subquery(self.pending_fetches().values("url")))
            .filter(author=None)
        )
        if kwargs.get("user"):
            qs.filter(watching=kwargs["user"])
        return qs

    def refetch_novel(self, novel_id):
        fic = _Fiction.objects.get(id=novel_id)
        if self.pending_fetches().filter(url=fic.url).count() > 0:
            self.logger.info(f"{fic.title} is already queued, skipping")
            return False
        else:
            self.logger.info(f"added {fic.title} to the queue")
            _Scrapes.objects.create(url=fic.url, parser_type_id=self.get_parser_id())
            return True

    def add_queue_events(self, *args, **kwargs):
        """Conditionally add a new pending fetch."""
        try:
            for novel in self.missing_novels(*args, **kwargs):
                self.logger.info(f"adding '{novel.title}' to the pending fetches")
                _Scrapes.objects.create(
                    url=novel.url, parser_type_id=self.get_parser_id()
                )

            return True
        except Exception:  # pragma: no cover
            self.logger.exception(f"failed to add a novel to scraping queue")

    def parse_novel_scrape(self, scrape_id: int):
        scrape = _Scrapes.objects.get(id=scrape_id)
        if scrape.http_code != 200:
            return False

        parse_log_dict = {"parser_id": self.get_parser_id(), "started": _timezone.now()}
        parse_log, created = _ParseLog.objects.get_or_create(
            scrape=scrape, defaults=parse_log_dict
        )
        if not created:
            _ParseLog.objects.filter(id=parse_log.id).update(**parse_log_dict)
            parse_log.refresh_from_db()

        try:
            fiction_remote_id = int(scrape.url.split("/")[-2])
            fiction, fic_created = _Fiction.objects.get_or_create(
                remote_id=fiction_remote_id, source_id=self.get_parser_id()
            )
        except (ValueError, IndexError, TypeError):
            self.logger.exception("couldn't determine remote id of the fiction")
            raise
        except _Fiction.MultipleObjectsReturned:
            self.logger.exception(
                f"There were multiple fictions in the queryset. Failing on possible parsing error"
            )
            raise

        tree = _html.fromstring(scrape.content)

        fiction.author = tree.xpath('//h4[@property="author"]//a/text()')[0]
        fiction.title = tree.xpath('//h1[@property="name"]/text()')[0]
        fiction.save()

        chapters = tree.xpath("//tr")
        modified_chapters = list()

        for chapter in chapters:
            url_element = chapter.xpath("./td/a/@href")
            if len(url_element) == 0:
                continue
            chapter_dict = dict()
            chapter_dict["url"] = self.BASE_URL + url_element[0]
            chapter_dict["title"] = (
                chapter.xpath("./td/a/text()")[0]
                .encode("raw-unicode-escape")
                .decode("unicode_escape")
                .strip()
            )

            try:
                remote_id = int(chapter_dict["url"].split("/")[-2])
                chap, created = _Chapter.objects.get_or_create(
                    fiction=fiction, remote_id=remote_id, defaults=chapter_dict
                )
            except (ValueError, IndexError, TypeError):
                self.logger.exception(
                    f"couldn't determine remote id of the chapter {chapter_dict['url']})"
                )
                raise

            modified = False
            if chapter_dict["title"] != chap.title:
                chap.title = chapter_dict["title"]
                chap.save()
                modified = True
            if chapter_dict["url"] != chapter_dict["url"]:
                chap.url = chapter_dict["url"]
                modified = True

            if created or modified:
                modified_chapters.append(chap.id)

        parse_log.finished = _timezone.now()
        parse_log.success = True

        modified_objects = {
            "types": ["fiction", "chapters"],
            "fictions": [fiction.id],
            "chapters": modified_chapters,
        }
        parse_log.modified_object = modified_objects
        parse_log.save()
        self.logger.info(
            f"modified  {len(modified_objects['chapters'])} for {fiction.title}"
        )
        return

    def novel_extractor(self):
        """Return False if no Parses were necessary. True if the parsing was successful."""
        pending_parses = self.all_pending_parses()

        if pending_parses.count() == 0:
            self.logger.info("no rrl novel page to parse")
            return False

        self.logger.info(f"found {pending_parses.count()} novel scrapes to parse!")

        success_monitor = True

        for scrape in pending_parses:
            self.logger.info(f"parsing {scrape.id}")

            tree = _html.fromstring(scrape.content)

            parse_log = _ParseLog.objects.create(
                scrape=scrape, parser_id=self.get_parser_id(), started=_timezone.now()
            )
            data_extracted = self._parse_fiction_page(tree, scrape.url)
            parse_log.finished = _timezone.now()
            if data_extracted:
                parse_log.success = success_monitor
            else:
                success_monitor = False  # pragma: no cover
            parse_log.save()
        return success_monitor

    def _parse_fiction_page(self, element, url):
        try:
            remote_id = url.split("/")[-2]
            fic, created = _Fiction.objects.get_or_create(url=url)
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
                chap, created = _Chapter.objects.get_or_create(
                     fiction=fic, remote_id=chap_remote_id, defaults={'url': chap_url}
                )
                chap.title = (
                    chapter.xpath("./td/a/text()")[0]
                    .encode("raw-unicode-escape")
                    .decode("unicode_escape")
                    .strip()
                )
                if not created:
                    chap.url = chap_url
                chap.save()
                created_chapters += 1

            fic.author = element.xpath('//h4[@property="author"]//a/text()')[0]
            fic.title = element.xpath('//h1[@property="name"]/text()')[0]
            fic.save()
            self.logger.info(
                f'updated content of "{fic.title}" and added {created_chapters}'
            )
            return True
        except Exception:  # pragma: no cover
            self.logger.exception("failed to parse chapter")
