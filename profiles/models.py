from django.shortcuts import reverse
from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4


class ProvidedUrl(models.Model):
    url = models.CharField(max_length=200)
    success = models.BooleanField(null=True, blank=True)
    scrape = models.ForeignKey(
        "scrapes.Scrapes", null=True, blank=True, on_delete=models.SET_NULL
    )
    parser = models.ForeignKey(
        "scrapes.Parser", null=True, blank=True, on_delete=models.SET_NULL
    )
    fiction = models.ForeignKey(
        "novels.Fiction", null=True, blank=True, on_delete=models.SET_NULL
    )
    job = models.ForeignKey("BulkWatchJob", on_delete=models.CASCADE)


class BulkWatchJob(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    @property
    def get_absolute_url(self):
        return reverse("profiles:bulk-watch-progress", kwargs={"job_id": self.pk})


class User(AbstractUser):
    COLOR_CHOICES = (
        ("cerulean", "cerulean"),
        ("cosmo", "cosmo"),
        ("cyborg", "cyborg"),
        ("darkly", "darkly (default)"),
        ("flatly", "flatly"),
        ("journal", "journal"),
        ("litera", "litera"),
        ("lumen", "lumen"),
        ("lux", "lux"),
        ("materia", "materia"),
        ("minty", "minty"),
        ("pulse", "pulse"),
        ("pulse", "pulse"),
        ("sandstone", "sandstone"),
        ("simplex", "simplex"),
        ("sketchy", "sketchy"),
        ("slate", "slate"),
        ("solar", "solar"),
        ("spacelab", "spacelab"),
        ("superhero", "superhero"),
        ("united", "united"),
        ("yeti", "yeti"),
    )

    login_token = models.UUIDField(default=uuid4, blank=True, null=True, editable=False)
    enable_login_token = models.BooleanField(default=False)
    internal_links = models.BooleanField(default=False)
    color_theme = models.CharField(
        default="darkly", choices=COLOR_CHOICES, max_length=50
    )


class ReadingProgress(models.Model):
    chapter = models.ForeignKey("novels.Chapter", on_delete=models.CASCADE)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    progress = models.IntegerField()
