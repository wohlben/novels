# Generated by Django 2.1.4 on 2018-12-27 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("profiles", "0004_auto_20181227_1437")]

    operations = [
        migrations.AddField(
            model_name="bulkwatchjob",
            name="processed",
            field=models.BooleanField(blank=True, null=True),
        )
    ]