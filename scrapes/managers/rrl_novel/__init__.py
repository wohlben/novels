from scrapes.models import Parser
from scrapes.managers.ScrapeManager import ScrapeManager
from .generator import RRLNovelGeneratorMixin
from .parser import RRLNovelParserMixin


class RRLNovelScraper(ScrapeManager, RRLNovelGeneratorMixin, RRLNovelParserMixin):
    parser_id = Parser.objects.get(name="rrl novel").id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
