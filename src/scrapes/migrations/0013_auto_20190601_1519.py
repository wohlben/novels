# Generated by Django 2.2.1 on 2019-06-01 15:19

from django.db import migrations


def fix_contents(apps, schema_editor):
    Scrapes = apps.get_model("scrapes", "Scrapes")
    all_scrapes = Scrapes.objects.exclude(content=None)
    for scrape in all_scrapes:
        scrape.content = (
            scrape.content
            .encode("raw-unicode-escape")
            .decode("unicode-escape")
        )
        scrape.save()
        


class Migration(migrations.Migration):

    dependencies = [
        ('scrapes', '0012_insert_snakey_parser'),
    ]

    operations = [
            migrations.RunPython(fix_contents, reverse_code=lambda x, y : None )
    ]
