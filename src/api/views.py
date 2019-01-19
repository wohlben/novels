from django_filters.rest_framework import DjangoFilterBackend
from api.serializers import (
    FictionListSerializer as _FictionListSerializer,
    FictionSerializer as _FictionSerializer,
    ChapterListSerializer as _ChapterListSerializer,
    ChapterSerializer as _ChapterSerializer,
    ReadingProgressSerializer as _ReadingProgressSerializer,
    ParserSerializer as _ParserSerialzer,
)
from novels.models import Fiction as _Fiction, Chapter as _Chapter
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

_managers = _Managers()


class FictionViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
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
            return HttpResponse(status=204)
        return HttpResponse(status=403)

    @action(detail=True, methods=["post"])
    def watch(self, request, pk=None):
        if request.user.is_authenticated:
            user = request.user
            fiction = self.get_object()
            watching = user.fiction_set.filter(id=pk).count()
            if watching >= 1:
                fiction.watching.remove(user)
            else:
                fiction.watching.add(user)
            return HttpResponse(status=204)
        return HttpResponse(status=403)


class ChapterViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
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
        self.request.POST.get()
        if request.user.has_perm("scrapes.view_system") and pk is not None:
            _managers.rrl_chapter.refetch_chapter(pk)
            return HttpResponse(status=204)
        return HttpResponse(status=403)


class ReadingProgressViewSet(viewsets.ModelViewSet):
    serializer_class = _ReadingProgressSerializer
    http_method_names = ["get", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("chapter",)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return _ReadingProgress.objects.filter(user=self.request.user)
        return _ReadingProgress.objects.none()


class ParserViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = _ParserSerialzer
    queryset = _Parser.objects.all()
    http_method_names = ("get", "post")

    @action(detail=False, methods=["post"])
    def delete_all_parses(self, request, pk=None, days=1):
        if request.user.has_perm("scrapes.view_system"):
            _ParseLog.objects.filter(
                started__gt=_timezone.now() - _timedelta(days=days)
            ).delete()
            _parsers_task()
            return HttpResponse(status=204)
        return HttpResponse(status=403)

    @action(detail=True, methods=["post"])
    def delete_parses(self, request, pk=None, days=1):
        if request.user.has_perm("scrapes.view_system"):
            _ParseLog.objects.filter(
                parser_id=pk, started__gt=_timezone.now() - _timedelta(days=days)
            ).delete()
            _parsers_task()
            return HttpResponse(status=204)
        return HttpResponse(status=403)
