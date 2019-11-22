from django.core.management.base import BaseCommand as _BaseCommand
from django.core import serializers as _serializers
from scrapes.models import Scrapes as _Scrapes, Parser as _Parser
from django.db.models import Count as _Count
from scrapes.models import Scrapes as _Scrapes


class Commands(_BaseCommand):
    help = "delete duplicate novels in the database"

    def handle(self, *args, **options):
        dups = _Scrapes.objects.exclude(content=None).exclude(url="https://www.royalroad.com/fictions/latest-updates").values('url').annotate(url_count=_Count('url')).filter(url_count__gt=1)
        while dups.count() > 0:
            urls = [c['url'] for c in dups]
            [_Scrapes.objects.filter(url=u).first().delete() for u in urls]
