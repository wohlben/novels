from scrapes.models import Scrapes
import logging


class ScrapeManager(object):
    logger = logging.getLogger("scrapes.tasks")

    def all_pending_parses(self):
        """Return the pending parses that this parser can handle."""
        return Scrapes.objects.filter(
            http_code=200, parser_type_id=self.parser_id, parselog__isnull=True
        )

    @staticmethod
    def scrape_queue():
        return Scrapes.objects.filter(http_code=None, content=None).order_by(
            "parser_type__weight", "id"
        )
