import django_filters
from .models import Fiction, Chapter


class FictionFilter(django_filters.FilterSet):
    watching = django_filters.Filter(method="watching_filter")
    populated = django_filters.Filter(method="populated_filter")
    updated = django_filters.Filter(method="updated_filter")

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
