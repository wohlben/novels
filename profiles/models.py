from django.shortcuts import reverse as _reverse
from django.db import models as _models
from django.contrib.auth.models import AbstractUser as _AbstractUser
from uuid import uuid4 as _uuid4


class ProvidedUrl(_models.Model):
    url = _models.CharField(max_length=200)
    success = _models.BooleanField(null=True, blank=True)
    scrape = _models.ForeignKey(
        "scrapes.Scrapes", null=True, blank=True, on_delete=_models.SET_NULL
    )
    parser = _models.ForeignKey(
        "scrapes.Parser", null=True, blank=True, on_delete=_models.SET_NULL
    )
    fiction = _models.ForeignKey(
        "novels.Fiction", null=True, blank=True, on_delete=_models.SET_NULL
    )
    job = _models.ForeignKey("BulkWatchJob", on_delete=_models.CASCADE)


class BulkWatchJob(_models.Model):
    user = _models.ForeignKey("User", on_delete=_models.CASCADE)

    @property
    def get_absolute_url(self):
        return _reverse("profiles:bulk-watch-progress", kwargs={"job_id": self.pk})


class User(_AbstractUser):
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

    login_token = _models.UUIDField(
        default=_uuid4, blank=True, null=True, editable=False
    )
    enable_login_token = _models.BooleanField(default=False)
    internal_links = _models.BooleanField(default=False)
    color_theme = _models.CharField(
        default="darkly", choices=COLOR_CHOICES, max_length=50
    )


class ReadingProgress(_models.Model):
    class Meta:
        unique_together = ("chapter", "user")

    chapter = _models.ForeignKey("novels.Chapter", on_delete=_models.CASCADE)
    user = _models.ForeignKey("User", on_delete=_models.CASCADE)
    progress = _models.IntegerField()
    timestamp = _models.DateTimeField(auto_now=True)

    @property
    def get_absolute_url(self):
        _reverse(
            "profiles:progress",
            kwargs={"chapter_id": self.id, "progress": self.progress},
        )
