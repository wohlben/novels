from django_filters import FilterSet as _FilterSet, Filter as _Filter
from django.db.models import Subquery as _Subquery
from .models import Fiction as _Fiction, Chapter as _Chapter


class FictionFilter(_FilterSet):
    watching = _Filter(method="watching_filter")
    populated = _Filter(method="populated_filter")
    updated = _Filter(method="updated_filter")

    class Meta:
        model = _Fiction
        fields = ["title", "watching"]

    def watching_filter(self, queryset, name, value):
        if self.data["user"].is_authenticated:
            return queryset.filter(watching=self.data["user"])
        return queryset.exclude()

    def populated_filter(self, queryset, name, value):
        return queryset.filter(
            id__in=_Chapter.objects.exclude(content=None).values("fiction")
        )

    def updated_filter(self, queryset, name, value):
        return queryset.filter(
            id__in=_Chapter.objects.order_by("-updated").values("fiction_id")[:50]
        )


class ChapterFilter(_FilterSet):
    watching = _Filter(method="watching_filter")

    def watching_filter(self, queryset, name, value):
        if self.data["user"].is_authenticated:
            return queryset.filter(
                fiction_id__in=_Subquery(
                    _Fiction.objects.filter(watching=self.data["user"]).values("id")
                )
            )
        else:
            return queryset.exclude()
