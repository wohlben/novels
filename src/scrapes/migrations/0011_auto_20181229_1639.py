# Generated by Django 2.1.4 on 2018-12-29 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("scrapes", "0010_auto_20181229_1637")]

    operations = [
        migrations.AlterModelOptions(
            name="scrapes",
            options={
                "permissions": (
                    ("force_fetch", "Allows a User to force a fetch from the source"),
                    ("view_system", "Allows the User to see the System views"),
                )
            },
        )
    ]