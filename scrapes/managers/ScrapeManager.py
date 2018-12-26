from scrapes.models import Scrapes, Parser
import logging
from django.utils import timezone
from datetime import timedelta


class ScrapeManager(object):
    logger = logging.getLogger("scrapes.tasks")
    parser_name = None
    parser_id = None

    def get_parser_id(self):
        if self.parser_id == None:
            self.parser_id = Parser.objects.get(name=self.parser_name).id
        return self.parser_id

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def all_pending_parses(self):
        """Return the pending parses that this parser can handle."""
        return Scrapes.objects.filter(
            http_code=200, parser_type_id=self.get_parser_id(), parselog__isnull=True
        )

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
