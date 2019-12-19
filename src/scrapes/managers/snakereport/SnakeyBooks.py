from lxml import html
import requests

from scrapes.managers.ScrapeManagerBase import ScrapeManagerBase as _ScrapeManagerBase
from novels.models import Chapter as _Chapter, Fiction as _Fiction
from scrapes.models import Scrapes as _Scrapes, Parser as _Parser


class SnakeyScraper(_ScrapeManagerBase):
    parser_name = "snek_report"

    def parse(self, **kwargs):
        if kwargs.get("scrape_id"):
            return self._parse_book(kwargs["scrape_id"])
        return self._parse_all_books()

    def _parse_book(self, scrape_id):
        scrape = _Scrapes.objects.get(id=scrape_id)
        book_tree = html.fromstring(scrape.content)
        for chapter in book_tree.xpath("//article"):
            chapter_title = chapter.xpath('.//h1[@class="entry-title"]/a/text()')[0]
            chapter_uri = chapter.xpath('.//h1[@class="entry-title"]/a/@href')[0]
            chapter_published = chapter.xpath('.//time[@class="published"]/@datetime')[
                0
            ]
            chapter_content = chapter.xpath('.//div[@class="sqs-block-content"]')[0]

    def _parse_all_books(self):
        for scrape in self.all_pending_parses():
            self._parse_book(scrape.id)

    def fetch_book(self, uri: str, fetch_reason=None) -> int:
        scrapes = _Scrapes.objects.filter(
            url__endswith=uri, parser_type_id=self.get_parser_id()
        )
        if scrapes.count() >= 1:
            scrape = scrapes.last()
        else:
            scrape = _Scrapes.objects.create(
                url=f"https://thesnekreport.com{uri}",
                added_reason=fetch_reason,
                parser_type_id=self.get_parser_id(),
            )

    def pending_fetches(self):
        return _Scrapes.objects.filter(parser_type_id=self.get_parser_id()).exclude(
            http_code=None
        )
