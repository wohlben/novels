"""Extraction of Data from basic scrapes."""
from scrapes.models import Scrapes
from novels.models import Chapter

__all__ = ['rrl_latest', 'rrl_novel', 'rrl_chapter', 'all_pending_parses', 'available_chapter_urls']


def all_pending_parses(parser_id):
    """Return the pending parses that this parser can handle."""
    return Scrapes.objects.filter(http_code=200, parser_type_id=parser_id, parselog__isnull=True)
