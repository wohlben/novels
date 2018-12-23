from .ScrapeManager import ScrapeManager
from .RRL import RRLLatestScraper, RRLNovelScraper, RRLChapterScraper

__all__ = [
    "Managers",
    "RRLNovelScraper",
    "RRLLatestScraper",
    "RRLChapterScraper",
    "ScrapeManager",
]


class Managers(object):
    def __init__(self, *args, **kwargs):
        self.manager = ScrapeManager()
        self.rrl_latest = RRLLatestScraper()
        self.rrl_novel = RRLNovelScraper()
        self.rrl_chapter = RRLChapterScraper()
