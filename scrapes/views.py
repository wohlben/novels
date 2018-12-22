from django.views.generic import TemplateView, FormView
from scrapes.models import ParseLog
from django.db.models import Count, F
from scrapes.managers import ScrapeManager, RRLNovelScraper, RRLChapterScraper
from scrapes.forms import RequeueNovelForm, RequeueChapterForm
from django.http import HttpResponseRedirect


class ParseLogListView(TemplateView):
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


class RequeueNovelComponent(FormView):
    form_class = RequeueNovelForm
    template_name = "scrapes/components/requeue_novel.html"

    def get_context_data(self):
        return {"novel_id": self.kwargs.get("novel_id")}

    def post(self, request, novel_id, *args, **kwargs):
        RRLNovelScraper().refetch_novel(novel_id)
        return HttpResponseRedirect("#")


class RequeueChapterComponent(FormView):
    form_class = RequeueChapterForm
    template_name = "scrapes/components/requeue_chapter.html"

    def get_context_data(self):
        return {"chapter_id": self.kwargs.get("chapter_id")}

    def post(self, request, chapter_id, *args, **kwargs):
        RRLChapterScraper().refetch_chapter(chapter_id)
        return HttpResponseRedirect("#")


class QueueView(TemplateView):
    template_name = "scrapes/lists/queue.html"

    def get_context_data(self, **kwargs):
        context = {
            "queue": ScrapeManager().scrape_queue().prefetch_related("parser_type")
        }
        return context


class HistoryView(TemplateView):
    template_name = "scrapes/lists/history.html"


class TestView(TemplateView):
    template_name = "base.html"
