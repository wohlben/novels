from datetime import datetime

from django.utils import timezone
from django_filters import FilterSet, BaseInFilter, NumberFilter, BooleanFilter

from novels.models import Fiction, Author, Chapter


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class MultipleFictionsFilter(FilterSet):
    ids = NumberInFilter(field_name="id", lookup_expr="in")
    watching = BooleanFilter(method="filter_watching")

    class Meta:
        model = Fiction
        fields = ["ids", "watching", "id"]

    def filter_watching(self, qs, name, value):
        return qs.filter(watching=self.request.user)


class MultipleAuthorsFilter(FilterSet):
    ids = NumberInFilter(field_name="id", lookup_expr="in")

    class Meta:
        model = Author
        fields = ["ids", "id"]


class MultipleChaptersFilter(FilterSet):
    ids = NumberInFilter(field_name="id", lookup_expr="in")

    class Meta:
        model = Chapter
        fields = ["ids", "id", "fiction", "fiction__author"]


class WatchingFilter(FilterSet):
    publishedSince = NumberFilter(field_name="published since", method="filter_published_since")
    publishedUpTo = NumberFilter(field_name="published up to", method="filter_published_up_to")

    class Meta:
        model = Chapter
        fields = ["publishedSince", "publishedUpTo"]

    def filter_published_since(self, qs, name, value):
        try:
            since = timezone.make_aware(datetime.fromtimestamp(value))
            return qs.filter(published__gt=since)
        except:
            return qs.none()

    def filter_published_up_to(self, qs, name, value):
        since = timezone.make_aware(datetime.fromtimestamp(value))
        return qs.filter(published__lt=since)
