from django_filters.rest_framework import DjangoFilterBackend
from api.serializers import (
    FictionListSerializer as _FictionListSerializer,
    UpdatedSerializer as _UpdatedSerializer,
    FictionSerializer as _FictionSerializer,
    ChapterListSerializer as _ChapterListSerializer,
    ChapterSerializer as _ChapterSerializer,
    ReadingProgressSerializer as _ReadingProgressSerializer,
    ParserSerializer as _ParserSerialzer,
    AuthorSerializer,
)
from novels.filters import ChapterFilter as _ChapterFilter
from novels.models import Fiction as _Fiction, Chapter as _Chapter, Author as _Author
from profiles.models import ReadingProgress as _ReadingProgress
from rest_framework import viewsets
from rest_framework.decorators import action
from api.pagination import VariablePagination
from django.utils import timezone as _timezone
from datetime import timedelta as _timedelta
from scrapes.models import ParseLog as _ParseLog, Parser as _Parser
from django.http import HttpResponse
from scrapes.tasks import parsers_task as _parsers_task
from scrapes.managers import Managers as _Managers
from rest_framework import mixins
from django.db.models import Max as _Max, Prefetch as _Prefetch, Subquery

from django.db import connection

_managers = _Managers()


class WatchingFictionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pagination_class = VariablePagination
    serializer_class = _UpdatedSerializer

    def get_queryset(self):
        prefetch = _Prefetch(
            "fiction", queryset=_Fiction.objects.only("title", "author", "id").prefetch_related("author")
        )

        qs = (
            _Chapter.objects.date_sorted()
            .prefetch_related(prefetch)
            .only("id", "title", "published", "fiction", "url", "discovered", "total_progress",)
        )
        qs = qs.add_progress(self.request.user.id)
        qs = qs.filter(fiction_id__in=Subquery(_Fiction.objects.filter(watching=self.request.user).only("id")))
        return qs


class AuthorViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = _Author.objects.all().order_by("name")
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("name",)
    pagination_class = VariablePagination
    serializer_class = AuthorSerializer


class FictionViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = _Fiction.objects.all().order_by("title")
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("author",)
    pagination_class = VariablePagination

    def get_serializer_class(self):
        if self.action == "list":
            return _FictionListSerializer
        else:
            return _FictionSerializer

    @action(detail=True, methods=["post"])
    def requeue(self, request, pk=None):
        if request.user.has_perm("scrapes.view_system") and pk is not None:
            _managers.rrl_novel.refetch_novel(pk)
            return HttpResponse(status=204, reason="queued novel anew")
        return HttpResponse(status=403, reason="missing system permissions")

    @action(detail=True, methods=["post"])
    def watch(self, request, pk=None):
        if request.user.is_authenticated:
            user = request.user
            fiction = self.get_object()
            watching = user.fiction_set.filter(id=pk).count()
            if watching >= 1:
                fiction.watching.remove(user)
                return HttpResponse(status=204, reason="removed from watching")
            fiction.watching.add(user)
            return HttpResponse(status=204, reason="added to watching")
        return HttpResponse(status=401, reason="not logged in")


class ChapterViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = _Chapter.objects.all().order_by("-id")
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("fiction",)

    def get_serializer_class(self):
        if self.action == "list":
            return _ChapterListSerializer
        else:
            return _ChapterSerializer

    @action(detail=True, methods=["post"])
    def requeue(self, request, pk=None):
        if request.user.has_perm("scrapes.view_system"):
            if pk is not None:
                _managers.rrl_chapter.refetch_chapter(pk)
                return HttpResponse(status=204, reason="queued chapter anew")
            return HttpResponse(status=400, reason="missing pk")
        return HttpResponse(status=403, reason="missing system permissions")


class ReadingProgressViewSet(viewsets.ModelViewSet):
    serializer_class = _ReadingProgressSerializer
    http_method_names = ["get", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("chapter",)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return _ReadingProgress.objects.filter(user=self.request.user)
        return _ReadingProgress.objects.none()


class ParserViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = _ParserSerialzer
    queryset = _Parser.objects.all()
    http_method_names = ("get", "post")

    @action(detail=False, methods=["post"])
    def delete_all_parses(self, request, pk=None, days=1):
        if request.user.has_perm("scrapes.view_system"):
            _ParseLog.objects.filter(started__gt=_timezone.now() - _timedelta(days=days)).delete()
            _parsers_task()
            return HttpResponse(status=204)
        return HttpResponse(status=403, reason="missing system permission")

    @action(detail=True, methods=["post"])
    def delete_parses(self, request, pk=None, days=1):
        if request.user.has_perm("scrapes.view_system"):
            _ParseLog.objects.filter(parser_id=pk, started__gt=_timezone.now() - _timedelta(days=days)).delete()
            _parsers_task()
            return HttpResponse(status=204)
        return HttpResponse(status=403, reason="missing system permission")
