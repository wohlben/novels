from django_filters import FilterSet, Filter
from django.db.models import Subquery
from .models import Fiction, Chapter


class FictionFilter(FilterSet):
    watching = Filter(method="watching_filter")
    populated = Filter(method="populated_filter")
    updated = Filter(method="updated_filter")

    class Meta:
        model = Fiction
        fields = ["title", "watching"]

    def watching_filter(self, queryset, name, value):
        if self.data["user"].is_authenticated:
            return queryset.filter(watching=self.data["user"])
        return queryset.exclude()

    def populated_filter(self, queryset, name, value):
        return queryset.filter(
            id__in=Chapter.objects.exclude(content=None).values("fiction")
        )

    def updated_filter(self, queryset, name, value):
        return queryset.filter(
            id__in=Chapter.objects.order_by("-updated").values("fiction_id")[:50]
        )


class ChapterFilter(FilterSet):
    watching = Filter(method="watching_filter")

    def watching_filter(self, queryset, name, value):
        if self.data["user"].is_authenticated:
            return queryset.filter(
                fiction_id__in=Subquery(
                    Fiction.objects.filter(watching=self.data["user"]).values("id")
                )
            )
        else:
            return queryset.exclude()
