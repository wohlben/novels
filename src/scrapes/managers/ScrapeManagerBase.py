from scrapes.models import Scrapes, Parser
import logging
from requests import get
from django.utils import timezone
from datetime import timedelta

from abc import ABC, abstractmethod
from django.conf import settings as _settings


class ScrapeManagerBase(ABC):
    logger = logging.getLogger("scrapes.tasks")
    parser_id = None  # type: int

    @property
    @abstractmethod
    def parser_name(self):
        pass

    @abstractmethod
    def parse(self):
        pass

    def get_parser_id(self):
        if self.parser_id is None:
            self.parser_id = Parser.objects.get(name=self.parser_name).id
        return self.parser_id

    def all_pending_parses(self):
        """Return the pending parses that this parser can handle."""
        return Scrapes.objects.filter(
            http_code=200, parser_type_id=self.get_parser_id(), parselog__isnull=True
        )

    def _fetch_from_source(self, scrape_id: int) -> int:
        scrape = Scrapes.objects.get(id=scrape_id)

        self.logger.info(f"fetching {scrape.url} for {scrape.id}")

        if _settings.TESTING:
            self.logger.info("not fetching in test mode...")
            return scrape.id

        with get(scrape.url) as page:  # pragma: no cover
            scrape.content = page.content
            scrape.http_code = page.status_code
            scrape.save()
            return scrape.id

    @staticmethod
    def scrape_queue():
        return Scrapes.objects.filter(http_code=None, content=None).order_by(
            "parser_type__weight", "id"
        )

    @staticmethod
    def last_scrapes():
        return (
            Scrapes.objects.exclude(http_code=None)
            .filter(last_change__gt=timezone.now() - timedelta(hours=1))
            .order_by("-last_change")[:5]
        )
