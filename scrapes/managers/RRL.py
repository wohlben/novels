from . import ScrapeManagerBase
from .rrl_novel import RRLNovelParserMixin, RRLNovelGeneratorMixin
from .rrl_latest import RRLLatestParserMixin, RRLLatestGeneratorMixin
from .RRLChapter import RRLChapterScraper

__all__ = ["RRLChapterScraper", "RRLNovelScraper", "RRLLatestScraper"]


class RRLNovelScraper(RRLNovelGeneratorMixin, RRLNovelParserMixin, ScrapeManagerBase):
    parser_name = "rrl novel"


class RRLLatestScraper(
    RRLLatestGeneratorMixin, RRLLatestParserMixin, ScrapeManagerBase
):
    parser_name = "rrl latest"
