# Generated by Django 2.1.4 on 2018-12-19 19:58

from django.db import migrations, models


def set_weights(apps, schema_editor):
    Parser = apps.get_model("scrapes", "Parser")
    parsers = {"rrl latest": 10, "rrl chapter": 30, "rrl novel": 20}
    for parser, weight in parsers.items():
        Parser.objects.filter(name=parser).update(weight=weight)


def reset_weights(apps, schema_editor):  # pragma: no cover
    Parser = apps.get_model("scrapes", "Parser")
    parsers = {"rrl latest": 50, "rrl chapter": 50, "rrl novel": 50}
    for parser, weight in parsers.items():
        Parser.objects.filter(name=parser).update(weight=weight)


class Migration(migrations.Migration):

    dependencies = [("scrapes", "0006_auto_20181217_1959")]

    operations = [
        migrations.AddField(
            model_name="parser", name="weight", field=models.IntegerField(default=50)
        ),
        migrations.RunPython(set_weights, reverse_code=reset_weights),
    ]
