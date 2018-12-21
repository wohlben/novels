from scrapes.models import Parser
from scrapes.managers.ScrapeManager import ScrapeManager
from .generator import RRLChapterGeneratorMixin
from .parser import RRLChapterParserMixin


class RRLChapterScraper(ScrapeManager, RRLChapterGeneratorMixin, RRLChapterParserMixin):
    parser_id = Parser.objects.get(name="rrl chapter").id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
