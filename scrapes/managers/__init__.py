from .ScrapeManager import ScrapeManager
from .rrl_novel import RRLNovelParserMixin, RRLNovelGeneratorMixin
from .rrl_latest import RRLLatestParserMixin, RRLLatestGeneratorMixin
from .rrl_chapter import RRLChapterGeneratorMixin, RRLChapterParserMixin

__all__ = ["Managers", "RRLNovelScraper", "RRLLatestScraper", "RRLChapterScraper", "ScrapeManager"]


class RRLNovelScraper(ScrapeManager, RRLNovelGeneratorMixin, RRLNovelParserMixin):
    parser_name = "rrl novel"

class RRLLatestScraper(ScrapeManager, RRLLatestGeneratorMixin, RRLLatestParserMixin):
    parser_name = "rrl latest"

class RRLChapterScraper(ScrapeManager, RRLChapterGeneratorMixin, RRLChapterParserMixin):
    parser_name = "rrl chapter"

class Managers(object):
    def __init__(self, *args, **kwargs):
        self.manager = ScrapeManager()
        self.rrl_latest = RRLLatestScraper()
        self.rrl_novel = RRLNovelScraper()
        self.rrl_chapter = RRLChapterScraper()
