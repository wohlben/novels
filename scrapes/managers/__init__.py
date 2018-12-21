from .rrl_latest import RRLLatestScraper
from .rrl_novel import RRLNovelScraper
from .rrl_chapter import RRLChapterScraper
from .ScrapeManager import ScrapeManager

__all__ = ["rrl_latest", "rrl_novel", "rrl_chapter"]

manager = ScrapeManager()
rrl_latest = RRLLatestScraper()
rrl_novel = RRLNovelScraper()
rrl_chapter = RRLChapterScraper()
