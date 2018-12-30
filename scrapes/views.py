from django.views.generic import TemplateView as _TemplateView, FormView as _FormView
from scrapes.models import ParseLog as _ParseLog
from django.db.models import Count as _Count, F as _F
from scrapes.managers import Managers as _Managers
from scrapes.forms import (
    RequeueNovelForm as _RequeueNovelForm,
    RequeueChapterForm as _RequeueChapterForm,
)
from django.http import HttpResponse as _HttpResponse
from django.contrib.auth.mixins import (
    PermissionRequiredMixin as _PermissionRequiredMixin,
)

_managers = _Managers()


class ParseLogListView(_PermissionRequiredMixin, _TemplateView):
    template_name = "scrapes/lists/log.html"
    permission_required = "scrapes.view_system"

    def get_context_data(self, **kwargs):
        context = {
            "parses": _ParseLog.objects.all()
            .order_by("-id")
            .select_related("parser")
            .annotate(
                added_count=_Count("added_by"),
                scrape_last_change=_F("scrape__last_change"),
            )
        }
        return context


class QueueView(_PermissionRequiredMixin, _TemplateView):
    template_name = "scrapes/lists/queue.html"
    permission_required = "scrapes.view_system"

    def get_context_data(self, **kwargs):
        context = {
            "queue": _managers.manager.scrape_queue().prefetch_related("parser_type"),
            "last_scrapes": reversed(
                _managers.manager.last_scrapes().prefetch_related("parser_type")
            ),
        }
        return context


class HistoryView(_PermissionRequiredMixin, _TemplateView):
    template_name = "scrapes/lists/history.html"
    permission_required = "scrapes.view_system"


class RequeueNovelComponent(_FormView):
    form_class = _RequeueNovelForm
    template_name = "scrapes/components/requeue_novel.html"

    def get_context_data(self):
        return {"novel_id": self.kwargs.get("novel_id")}

    def post(self, request, *args, **kwargs):
        novel_id = kwargs.get("novel_id")
        if request.user.is_authenticated:
            _managers.rrl_novel.refetch_novel(novel_id)
            return _HttpResponse(status=201)
        return _HttpResponse(status=403)


class RequeueChapterComponent(_FormView):
    form_class = _RequeueChapterForm
    template_name = "scrapes/components/requeue_chapter.html"

    def get_context_data(self):
        return {"chapter_id": self.kwargs.get("chapter_id")}

    def post(self, request, *args, **kwargs):
        chapter_id = kwargs.get("chapter_id")
        if request.user.is_authenticated:
            _managers.rrl_chapter.refetch_chapter(chapter_id)
            return _HttpResponse(status=201)
        return _HttpResponse(status=403)


class TestView(_TemplateView):
    template_name = "base.html"
