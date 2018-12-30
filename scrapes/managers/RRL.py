from . import ScrapeManagerBase
from .rrl_novel import RRLNovelParserMixin, RRLNovelGeneratorMixin
from .RRLChapter import RRLChapterScraper
from .RRLLatest import RRLLatestScraper

__all__ = ["RRLChapterScraper", "RRLNovelScraper", "RRLLatestScraper"]


class RRLNovelScraper(RRLNovelGeneratorMixin, RRLNovelParserMixin, ScrapeManagerBase):
    parser_name = "rrl novel"
