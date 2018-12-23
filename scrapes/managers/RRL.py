from . import ScrapeManager
from .rrl_novel import RRLNovelParserMixin, RRLNovelGeneratorMixin
from .rrl_latest import RRLLatestParserMixin, RRLLatestGeneratorMixin
from .rrl_chapter import RRLChapterGeneratorMixin, RRLChapterParserMixin


class RRLNovelScraper(ScrapeManager, RRLNovelGeneratorMixin, RRLNovelParserMixin):
    parser_name = "rrl novel"


class RRLLatestScraper(ScrapeManager, RRLLatestGeneratorMixin, RRLLatestParserMixin):
    parser_name = "rrl latest"


class RRLChapterScraper(ScrapeManager, RRLChapterGeneratorMixin, RRLChapterParserMixin):
    parser_name = "rrl chapter"
