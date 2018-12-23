"""discovery for pending rrl latest parses and parsing them into fictions and novels."""
from lxml import html
from scrapes.models import ParseLog
from novels.models import Fiction, Chapter
from django.utils import timezone


class RRLLatestParserMixin(object):
    BASE_URL = "https://www.royalroad.com"

    def latest_extractor(self):
        """Return False if no Parses were necessary, True the parsing was successful."""
        pending_parses = self.all_pending_parses()

        if pending_parses.count() == 0:
            self.logger.info("no rrl latest page to parse")
            return False

        self.logger.info(f"found {pending_parses.count()} scrapes to parse!")

        for scrape in pending_parses:
            self.logger.info(f"parsing {scrape.id}")

            tree = html.fromstring(scrape.content)

            parse_log = ParseLog.objects.create(
                scrape=scrape, parser_id=self.get_parser_id(), started=timezone.now()
            )

            novels = self._parse_fictions(tree)

            for novel, html_element in novels:
                self._parse_chapters(html_element, novel)

        parse_log.finished = timezone.now()
        parse_log.success = True
        parse_log.save()

        return True

    def _parse_chapters(self, element, fiction):
        added_chapters = 0
        updated_chapters = 0
        chapters = element.xpath('.//li[@class="list-item"]')
        for element in chapters:
            try:
                chapter = {}
                chapter["fiction"] = fiction
                path = element.xpath("./a/@href")[0]
                chapter["url"] = f"{self.BASE_URL}{path}"
                chapter["remote_id"] = int(path.split("/")[5])
                chapter["title"] = element.xpath("./a/span/text()")[0]
                published_relative = element.xpath(".//time/text()")[0]
                chap, created = Chapter.objects.get_or_create(
                    remote_id=chapter["remote_id"],
                    defaults={**chapter, "published_relative": published_relative},
                )
                if created:
                    added_chapters += 1
                else:
                    updated_chapters += 1
                    Chapter.objects.filter(id=chap.id).update(**chapter)

            except Exception:  # pragma: no cover
                self.logger.exception(f"failed to parse a chapter in {fiction}")
        if added_chapters + updated_chapters == len(chapters):
            self.logger.info(
                f"added {added_chapters} and updated {updated_chapters} for {fiction.title}"
            )
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
        for element in fictions:
            try:
                fiction = {}
                fiction["pic_url"] = element.xpath("./figure/img/@src")[0]
                fiction["title"] = element.xpath(
                    './/h2[@class="fiction-title"]/a/text()'
                )[0]
                path = element.xpath('.//h2[@class="fiction-title"]/a/@href')[0]
                fiction["url"] = f"{self.BASE_URL}{path}"
                fiction["remote_id"] = int(path.split("/")[2])
                fic, created = Fiction.objects.get_or_create(
                    url=fiction["url"], defaults=fiction
                )
                if created:
                    created_fictions += 1
                else:
                    updated_fictions += 1
                    Fiction.objects.filter(id=fic.id).update(**fiction)

                yield (fic, element)
            except Exception:  # pragma: no cover
                self.logger.exception("failed to parse a novel")
        if created_fictions + updated_fictions == expected_fictions:
            self.logger.info(f"added {created_fictions} and updated {updated_fictions}")
        else:
            self.logger.warning(
                f"expected {expected_fictions}, but only got {created_fictions} adds and {updated_fictions} updates parsing latest"
            )
