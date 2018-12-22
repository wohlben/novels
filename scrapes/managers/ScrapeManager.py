from scrapes.models import Scrapes, Parser
import logging


class ScrapeManager(object):
    logger = logging.getLogger("scrapes.tasks")
    parser_name = None

    def __init__(self, *args,**kwargs):

        if self.parser_name:
            self.parser_id = Parser.objects.get(name=self.parser_name).id


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
