# Generated by Django 2.1.4 on 2018-12-28 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("profiles", "0005_bulkwatchjob_processed")]

    operations = [migrations.RemoveField(model_name="bulkwatchjob", name="processed")]
