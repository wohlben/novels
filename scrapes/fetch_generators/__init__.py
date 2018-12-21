"""Generate pending fetches for various types of content."""
from scrapes.models import Scrapes, Parser

_parser_names = ["rrl latest", "rrl chapter", "rrl novel"]
_parsers = Parser.objects.filter(name__in=_parser_names)

__all__ = [
    *[f"{pn} generator".replace(" ", "_") for pn in _parser_names],
    "scrape_queue",
    "PARSERS",
]

PARSERS = {parser.name: parser.id for parser in _parsers}

def scrape_queue():
    return Scrapes.objects.filter(http_code=None, content=None).order_by(
        "parser_type__weight", "id"
    )
