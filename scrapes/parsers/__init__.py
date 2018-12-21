"""Extraction of Data from basic scrapes."""
from scrapes.models import Scrapes, Parser

_parser_names = ["rrl latest", "rrl chapter", "rrl novel"]
_parsers = Parser.objects.filter(name__in=_parser_names)

__all__ = [
    *[f"{pn} parser".replace(" ", "_") for pn in _parser_names],
    "all_pending_parses",
    "available_chapter_urls",
    "PARSERS",
]

PARSERS = {parser.name: parser.id for parser in _parsers}


def all_pending_parses(parser_id):
    """Return the pending parses that this parser can handle."""
    return Scrapes.objects.filter(
        http_code=200, parser_type_id=parser_id, parselog__isnull=True
    )
