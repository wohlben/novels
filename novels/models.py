"""Modeldefinitions for the novel app."""
from django.shortcuts import reverse as _reverse
from django.db import models as _models
from profiles.models import ReadingProgress as _ReadingProgress


class _FictionQS(_models.QuerySet):
    def add_chapter_count(self):
        return super().annotate(
            chapters=_models.Count(
                "chapter", filter=_models.Q(chapter__fiction=_models.F("id"))
            )
        )

    def add_read_count(self, user_id):
        return super().annotate(
            read=_models.Count(
                "chapter",
                filter=_models.Q(
                    chapter__fiction=_models.F("id"),
                    chapter__readingprogress__user_id=user_id,
                ),
            )
        )


class Fiction(_models.Model):
    """Fiction database model."""

    objects = _FictionQS.as_manager()

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

    def unread_chapters(self, user_id):
        return (
            self.chapter_set.add_progress(user_id)
            .filter(
                _models.Q(progress__lt=_models.F("total_progress"))
                | _models.Q(progress=None)
            )
            .count()
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
    word_count = _models.IntegerField(blank=True, null=True)
    url = _models.TextField()

    def __str__(self):
        return self.title

    @property
    def get_sort_date(self):
        if self.published:
            return self.published
        return self.discovered

    def get_relevant_chapters(self, user_id):
        return (
            Chapter.objects.filter(fiction=self.fiction)
            .date_sorted(order="")
            .add_progress(user_id)
            .filter(
                _models.Q(progress__lt=_models.F("total_progress"))
                | _models.Q(progress=None)
            )
        )

    def get_unread_following_chapters(self, user_id):
        sort_date = self.get_sort_date
        return self.get_relevant_chapters(user_id).filter(sort_date__gt=sort_date)

    def get_unread_previous_chapters(self, user_id):
        sort_date = self.get_sort_date
        return self.get_relevant_chapters(user_id).filter(sort_date__lt=sort_date)

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
                .date_sorted(order="")
                .filter(sort_date__gt=sort_date)
                .first()
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
                .date_sorted(order="")
                .filter(sort_date__lt=sort_date)
                .last()
            )
        except ValueError:
            return


class Highlight(_models.Model):
    chapter = _models.ForeignKey("Chapter", on_delete=_models.CASCADE)
    sentence = _models.TextField()

    def __str__(self):
        return self.sentence
