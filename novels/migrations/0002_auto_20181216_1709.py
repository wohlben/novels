# Generated by Django 2.1.2 on 2018-12-16 17:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('novels', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={'ordering': ['published', 'id']},
        ),
        migrations.AddField(
            model_name='fiction',
            name='watching',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
