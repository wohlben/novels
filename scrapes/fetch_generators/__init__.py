"""Generate pending fetches for various types of content."""
from scrapes.models import Scrapes

__all__ = ["rrl_chapter_generator", "rrl_novel_generator", "rrl_latest_generator", 'scrape_queue']


def scrape_queue():
    return Scrapes.objects.filter(http_code=None, content=None).order_by('parser_type__weight', 'id')
