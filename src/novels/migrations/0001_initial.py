# Generated by Django 2.1.2 on 2018-10-13 19:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Chapter",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.TextField(blank=True, null=True)),
                ("remote_id", models.TextField(blank=True, null=True)),
                ("content", models.TextField(blank=True, null=True)),
                ("published", models.DateTimeField(blank=True, null=True)),
                ("published_relative", models.TextField(blank=True, null=True)),
                ("discovered", models.DateTimeField(auto_now_add=True)),
                ("url", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Fiction",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("pic_url", models.TextField(blank=True, null=True)),
                ("pic", models.BinaryField(blank=True, null=True)),
                ("title", models.TextField(blank=True)),
                ("url", models.TextField()),
                ("remote_id", models.TextField(blank=True, null=True)),
                ("author", models.TextField(blank=True, null=True)),
                ("monitored", models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name="chapter",
            name="fiction",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="novels.Fiction"
            ),
        ),
    ]
