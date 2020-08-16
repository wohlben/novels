# Generated by Django 3.0.8 on 2020-08-01 08:38

from django.db import migrations, models
import django.db.models.deletion
from scrapes import tasks
from lxml import html
from requests import get


def set_author_obj(apps, schema_editor):
    Author = apps.get_model("novels", "Author")
    Fiction = apps.get_model("novels", "Fiction")
    Scrapes = apps.get_model("scrapes", "Scrapes")
    Parser = apps.get_model("scrapes", "Parser")
    novelParser = Parser.objects.get(name="rrl novel")

    for fic in Fiction.objects.filter(source=novelParser).exclude(author=None).iterator():
        try:
            author = Author.objects.get(name=fic.author)
            fic.author_obj = author
            fic.save()
        except Exception as e:
            scrape, created = Scrapes.objects.get_or_create(
                url=fic.url, parser_type=novelParser, defaults={"added_reason": "migration"}
            )
            if created or scrape.content is None:
                with get(scrape.url) as page:
                    scrape.http_code = page.status_code
                    scrape.content = page.text
                    scrape.save()
            tree = html.fromstring(scrape.content)
            author_name = tree.xpath('//h4[@property="author"]//a/text()')[0]
            author_url = tree.xpath('//h4[@property="author"]//a/@href')[0]
            author_remote_id = author_url.split("/")[-1]
            author, created = Author.objects.get_or_create(
                defaults={"url": author_url, "name": author_name,}, remote_id=author_remote_id
            )
            if created:
                fic.author_obj = author
                fic.save()
                print("created " + author_name)


def rollback(apps, schema_editor):
    # we created the column in same migration, so its gonna be gone anyway
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("novels", "0013_author"),
    ]

    operations = [
        migrations.AddField(
            model_name="fiction",
            name="author_obj",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="novels.Author"
            ),
        ),
        migrations.RunPython(set_author_obj, rollback),
    ]
