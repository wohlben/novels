from scrapes.managers.ScrapeManager import ScrapeManager
from .generator import RRLChapterGeneratorMixin
from .parser import RRLChapterParserMixin


class RRLChapterScraper(ScrapeManager, RRLChapterGeneratorMixin, RRLChapterParserMixin):
    parser_name = "rrl chapter"
