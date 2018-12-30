"""Modeldefinitions for the novel app."""
from django.shortcuts import reverse as _reverse
from django.db import models as _models
from profiles.models import ReadingProgress as _ReadingProgress


class Fiction(_models.Model):
    """Fiction database model."""

    pic_url = _models.TextField(blank=True, null=True)
    pic = _models.BinaryField(blank=True, null=True)
    title = _models.TextField(blank=True)
    url = _models.TextField()
    remote_id = _models.TextField(blank=True, null=True)
    author = _models.TextField(blank=True, null=True)

    watching = _models.ManyToManyField("profiles.User")

    source = _models.ForeignKey(
        "scrapes.Parser", on_delete=_models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return self.title

    @property
    def get_absolute_url(self):
        return _reverse("novels:novel", kwargs={"novel_id": self.pk})


class ChapterQS(_models.QuerySet):
    def date_sorted(self):
        return (
            super()
            .annotate(
                sort_date=_models.Case(
                    _models.When(published=None, then=_models.F("discovered")),
                    default=_models.F("published"),
                )
            )
            .order_by("-sort_date")
        )

    def add_progress(self, user_id):
        annotation = _ReadingProgress.objects.filter(
            user=user_id, chapter=_models.OuterRef("id")
        ).values("progress")
        return super().annotate(progress=_models.Subquery(annotation))


class Chapter(_models.Model):
    """Chapter database model."""

    objects = ChapterQS.as_manager()

    fiction = _models.ForeignKey("Fiction", on_delete=_models.CASCADE)
    title = _models.TextField(blank=True, null=True)
    remote_id = _models.TextField(blank=True, null=True)
    content = _models.TextField(blank=True, null=True)
    total_progress = _models.IntegerField(blank=True, null=True)
    published = _models.DateTimeField(blank=True, null=True)
    published_relative = _models.TextField(blank=True, null=True)
    updated = _models.DateTimeField(auto_now=True)
    discovered = _models.DateTimeField(auto_now_add=True)
    url = _models.TextField()

    @property
    def get_absolute_url(self):
        return _reverse("novels:chapter", kwargs={"chapter_id": self.pk})
