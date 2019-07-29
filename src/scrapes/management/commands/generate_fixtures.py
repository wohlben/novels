from django.core.management.base import BaseCommand as _BaseCommand
from django.core import serializers as _serializers
from scrapes.models import Scrapes as _Scrapes, Parser as _Parser
from datetime import date


class Command(_BaseCommand):
    help = "generate a new testing fixture"

    def handle(self, *args, **options):
        today = date.today().strftime("%Y_%m_%d")
        filename = f"scrapes/fixtures/{today}_scrapes.json"
        scrapes = []
        for p in _Parser.objects.all():
            scrapes.append(_Scrapes.objects.exclude(content=None).filter(parser_type_id=p.id).order_by('-id').first())

        with open(filename, "w+") as f:
            f.write(_serializers.serialize("json", scrapes))
        self.stdout.write(self.style.SUCCESS(f"saved file to {filename}"))
