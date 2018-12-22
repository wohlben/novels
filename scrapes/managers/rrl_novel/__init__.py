from scrapes.managers.ScrapeManager import ScrapeManager
from .generator import RRLNovelGeneratorMixin
from .parser import RRLNovelParserMixin


class RRLNovelScraper(ScrapeManager, RRLNovelGeneratorMixin, RRLNovelParserMixin):
    parser_name = "rrl novel"
