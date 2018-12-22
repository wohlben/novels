from .rrl_latest import RRLLatestScraper
from .rrl_novel import RRLNovelScraper
from .rrl_chapter import RRLChapterScraper
from .ScrapeManager import ScrapeManager

__all__ = ["rrl_latest", "rrl_novel", "rrl_chapter"]

class Managers(object):
    def __init__(self, *args, **kwargs):
        self.manager = ScrapeManager()
        self.rrl_latest = RRLLatestScraper()
        self.rrl_novel = RRLNovelScraper()
        self.rrl_chapter = RRLChapterScraper()
