from scrapes.managers.ScrapeManager import ScrapeManager
from .generator import RRLLatestGeneratorMixin
from .parser import RRLLatestParserMixin


class RRLLatestScraper(ScrapeManager, RRLLatestGeneratorMixin, RRLLatestParserMixin):
    parser_name = "rrl latest"


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
