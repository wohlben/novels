from django.core.management import BaseCommand
from django.db.models import Count as _Count

from novels.models import Fiction, Chapter
from scrapes.models import Scrapes as _Scrapes


class Command(BaseCommand):
    help = "delete duplicate novels in the database"

    def handle(self, *args, **options):
        dups = (
            Chapter.objects.values("remote_id")
            .annotate(remote_id_count=_Count("remote_id"))
            .filter(remote_id_count__gt=1)
        )
        for i in dups:
            cdups = Chapter.objects.filter(remote_id=i["remote_id"])
            for index, d in enumerate(cdups):
                if index == 0:
                    print("not deleting first")
                    continue
                print("deleting " + d.title)
                d.delete()

        novel_dups = (
            Fiction.objects.values("remote_id")
            .annotate(remote_id_count=_Count("remote_id"))
            .filter(remote_id_count__gt=1)
        )
        print(f"deleting {novel_dups.count()}")
        for i in novel_dups:
            cdups = Fiction.objects.filter(remote_id=i["remote_id"])
            for index, d in enumerate(cdups):
                if index == 0:
                    print("not deleting first")
                    continue
                print("deleting " + d.title)
                d.delete()
