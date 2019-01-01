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

    def get_last_read_chapter(self, user_id):
        qs = (
            Chapter.objects.filter(fiction=self)
            .date_sorted(order="")
            .add_progress(user_id)
            .exclude(progress=None)
        )
        if len(qs) >= 1:
            return qs.last()
        else:
            return None

    @property
    def get_absolute_url(self):
        return _reverse("novels:novel", kwargs={"novel_id": self.pk})


class _ChapterQS(_models.QuerySet):
    def date_sorted(self, order="-"):
        return (
            super()
            .annotate(
                sort_date=_models.Case(
                    _models.When(published=None, then=_models.F("discovered")),
                    default=_models.F("published"),
                )
            )
            .order_by(f"{order}sort_date")
        )

    def add_progress(self, user_id):
        annotation = _ReadingProgress.objects.filter(
            user=user_id, chapter=_models.OuterRef("id")
        )
        return super().annotate(
            progress=_models.Subquery(annotation.values("progress")),
            timestamp=_models.Subquery(annotation.values("timestamp")),
        )


class Chapter(_models.Model):
    """Chapter database model."""

    objects = _ChapterQS.as_manager()

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

    def __str__(self):
        return self.title

    def get_unread_previous_chapters(self, user_id):
        sort_date = self.published
        if not sort_date:
            sort_date = self.discovered
        return (
            Chapter.objects.filter(fiction=self.fiction)
            .date_sorted(order="")
            .add_progress(user_id)
            .filter(
                _models.Q(progress__lt=_models.F("total_progress"))
                | _models.Q(progress=None)
            )
            .filter(sort_date__lt=sort_date)
        )

    @property
    def get_absolute_url(self):
        return _reverse("novels:chapter", kwargs={"chapter_id": self.pk})

    @property
    def get_next_chapter(self):
        try:
            sort_date = self.published
            if not sort_date:
                sort_date = self.discovered

            return (
                Chapter.objects.filter(fiction=self.fiction)
                .date_sorted()
                .filter(sort_date__gt=sort_date)
                .last()  # date_sorted returns descending chapters!
            )
        except ValueError:
            return

    @property
    def get_previous_chapter(self):
        try:
            sort_date = self.published
            if not sort_date:
                sort_date = self.discovered
            return (
                Chapter.objects.filter(fiction=self.fiction)
                .date_sorted()
                .filter(sort_date__lt=sort_date)
                .first()
            )
        except ValueError:
            return
