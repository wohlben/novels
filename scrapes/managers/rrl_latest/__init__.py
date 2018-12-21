from scrapes.models import Parser
from scrapes.managers.ScrapeManager import ScrapeManager
from .generator import RRLLatestGeneratorMixin
from .parser import RRLLatestParserMixin


class RRLLatestScraper(ScrapeManager, RRLLatestGeneratorMixin, RRLLatestParserMixin):
    parser_id = Parser.objects.get(name="rrl latest").id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
