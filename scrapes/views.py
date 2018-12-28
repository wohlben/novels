from django.views.generic import TemplateView, FormView
from scrapes.models import ParseLog
from django.db.models import Count, F
from scrapes.managers import Managers
from scrapes.forms import RequeueNovelForm, RequeueChapterForm
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

managers = Managers()


class ParseLogListView(LoginRequiredMixin, TemplateView):
    template_name = "scrapes/lists/log.html"

    def get_context_data(self, **kwargs):
        context = {
            "parses": ParseLog.objects.all()
            .order_by("-id")
            .select_related("parser")
            .annotate(
                added_count=Count("added_by"),
                scrape_last_change=F("scrape__last_change"),
            )
        }
        return context


class QueueView(LoginRequiredMixin, TemplateView):
    template_name = "scrapes/lists/queue.html"

    def get_context_data(self, **kwargs):
        context = {
            "queue": managers.manager.scrape_queue().prefetch_related("parser_type"),
            "last_scrapes": reversed(
                managers.manager.last_scrapes().prefetch_related("parser_type")
            ),
        }
        return context


class HistoryView(LoginRequiredMixin, TemplateView):
    template_name = "scrapes/lists/history.html"


class RequeueNovelComponent(LoginRequiredMixin, FormView):
    form_class = RequeueNovelForm
    template_name = "scrapes/components/requeue_novel.html"

    def handle_no_permission(self):
        return HttpResponse(status=200)

    def get_context_data(self):
        return {"novel_id": self.kwargs.get("novel_id")}

    def post(self, request, novel_id, *args, **kwargs):
        managers.rrl_novel.refetch_novel(novel_id)
        return HttpResponse(status=201)


class RequeueChapterComponent(LoginRequiredMixin, FormView):
    form_class = RequeueChapterForm
    template_name = "scrapes/components/requeue_chapter.html"

    def handle_no_permission(self):
        return HttpResponse(status=200)

    def get_context_data(self):
        return {"chapter_id": self.kwargs.get("chapter_id")}

    def post(self, request, chapter_id, *args, **kwargs):
        managers.rrl_chapter.refetch_chapter(chapter_id)
        return HttpResponse(status=201)


class TestView(TemplateView):
    template_name = "base.html"
