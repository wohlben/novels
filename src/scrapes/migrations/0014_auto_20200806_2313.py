# Generated by Django 3.1 on 2020-08-06 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scrapes", "0013_auto_20190601_1520"),
    ]

    operations = [
        migrations.AlterField(
            model_name="parselog", name="modified_object", field=models.JSONField(blank=True, null=True),
        ),
    ]