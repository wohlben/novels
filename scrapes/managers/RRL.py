from . import ScrapeManagerBase
from .rrl_novel import RRLNovelParserMixin, RRLNovelGeneratorMixin
from .rrl_latest import RRLLatestParserMixin, RRLLatestGeneratorMixin
from .rrl_chapter import RRLChapterGeneratorMixin, RRLChapterParserMixin


class RRLNovelScraper(RRLNovelGeneratorMixin, RRLNovelParserMixin, ScrapeManagerBase):
    parser_name = "rrl novel"


class RRLLatestScraper(
    RRLLatestGeneratorMixin, RRLLatestParserMixin, ScrapeManagerBase
):
    parser_name = "rrl latest"


class RRLChapterScraper(
    RRLChapterGeneratorMixin, RRLChapterParserMixin, ScrapeManagerBase
):
    parser_name = "rrl chapter"
