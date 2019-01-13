from django_filters.rest_framework import DjangoFilterBackend
from api.serializers import (
    FictionListSerializer as _FictionListSerializer,
    FictionSerializer as _FictionSerializer,
    ChapterListSerializer as _ChapterListSerializer,
    ChapterSerializer as _ChapterSerializer,
    ReadingProgressSerializer as _ReadingProgressSerializer,
)
from novels.models import Fiction as _Fiction, Chapter as _Chapter
from profiles.models import ReadingProgress as _ReadingProgress
from rest_framework import viewsets
from api.pagination import VariablePagination

import logging

logger = logging.getLogger("serializers")


class FictionViewSet(viewsets.ModelViewSet):
    queryset = _Fiction.objects.all().order_by("title")
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("author",)
    pagination_class = VariablePagination
    http_method_names = ("get",)

    def get_serializer_class(self):
        if self.action == "list":
            return _FictionListSerializer
        else:
            return _FictionSerializer


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = _Chapter.objects.all().order_by("-id")
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("fiction",)
    http_method_names = ("get",)

    def get_serializer_class(self):
        if self.action == "list":
            return _ChapterListSerializer
        else:
            return _ChapterSerializer


class ReadingProgressViewSet(viewsets.ModelViewSet):
    serializer_class = _ReadingProgressSerializer
    http_method_names = ["get", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("chapter",)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return _ReadingProgress.objects.filter(user=self.request.user)
        return _ReadingProgress.objects.none()
