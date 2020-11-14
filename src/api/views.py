from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from api.filters import MultipleFictionsFilter, MultipleAuthorsFilter, MultipleChaptersFilter, WatchingFilter
from api.serializers import (
    FictionListSerializer as _FictionListSerializer,
    UpdatedSerializer as _UpdatedSerializer,
    FictionSerializer as _FictionSerializer,
    ChapterListSerializer as _ChapterListSerializer,
    ChapterSerializer as _ChapterSerializer,
    ReadingProgressSerializer as _ReadingProgressSerializer,
    ParserSerializer as _ParserSerializer,
    AuthorSerializer,
    AuthorDetailSerializer,
    FictionSearchSerializer,
)
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


_managers = _Managers()


class WatchingFictionViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = VariablePagination
    serializer_class = _UpdatedSerializer
    filter_backends = (DjangoFilterBackend,)

    filter_class = WatchingFilter

    def get_queryset(self):
        qs = (
            _Chapter.objects.date_sorted()
            .prefetch_related("fiction")
            .add_progress(self.request.user.id)
            .only("id", "title", "published", "fiction", "url", "discovered")
        )
        qs = qs.filter(fiction__watching=self.request.user)
        return qs


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = _Author.objects.all().order_by("name")
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("name",)
    filter_class = MultipleAuthorsFilter

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related("fiction_set")

    def get_serializer_class(self):
        if self.action == "list":
            return AuthorSerializer
        else:
            return AuthorDetailSerializer


class SearchViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = FictionSearchSerializer

    @method_decorator(cache_page(60))
    @method_decorator(vary_on_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = _Fiction.objects.add_chapter_count().exclude(chapters__lte=10).all().prefetch_related("author")
        if self.request.user.is_authenticated:
            qs = qs.add_watched(self.request.user)
        return qs


class FictionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = _Fiction.objects.all().order_by("title")
    filter_backends = (DjangoFilterBackend,)
    filter_class = MultipleFictionsFilter
    pagination_class = VariablePagination

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action != "list":
            qs = qs.prefetch_related(
                Prefetch("chapter_set", queryset=_Chapter.objects.order_by("published").exclude(published=None))
            )
        qs = qs.add_watched(self.request.user)
        qs = qs.add_chapter_count()
        qs = qs.add_read_count(self.request.user.id)
        return qs

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
        return HttpResponse(status=403, content="you're not an admin mate")

    @action(detail=True, methods=["post"])
    def watch(self, request, pk=None):
        if request.user.is_authenticated:
            user = request.user
            fiction = self.get_object()
            watching = user.fiction_set.filter(id=pk).count()
            if watching >= 1:
                fiction.watching.remove(user)
                return Response({"status": "removed"}, status=200)
            fiction.watching.add(user)
            return Response({"status": "added"}, status=200)
        return HttpResponse(status=401, reason="not logged in", content="dude, you're not even logged in")


class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = _Chapter.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("fiction",)
    pagination_class = None
    filter_class = MultipleChaptersFilter

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.add_progress(self.request.user.id)
        if self.action == "list":
            qs = qs.prefetch_related("fiction")
            qs = qs.only("id", "title", "published", "discovered", "fiction")
        return qs

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

    @action(detail=True, methods=["post"])
    def progress(self, request, pk=None):
        serializer = _ReadingProgressSerializer(data=request.data)
        if serializer.is_valid() and pk is not None:
            progress, created = _ReadingProgress.objects.get_or_create(
                chapter_id=pk, user=self.request.user, defaults={"progress": serializer.data["progress"]}
            )
            if not created:
                progress.progress = serializer.data["progress"]
                progress.save()
                return HttpResponse(status=204, reason="updated")
            return HttpResponse(status=201, reason="created")
        return HttpResponse(status=400, reason="invalid data or missing pk")


class ReadingProgressViewSet(viewsets.ModelViewSet):
    serializer_class = _ReadingProgressSerializer
    http_method_names = ["get", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("chapter",)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return _ReadingProgress.objects.filter(user=self.request.user)
        return _ReadingProgress.objects.none()


class ParserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = _ParserSerializer
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
