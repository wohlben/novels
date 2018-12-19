from django.views.generic import TemplateView
from scrapes.models import Parser, ParseLog
from django.db.models import Count, F
from scrapes.fetch_generators import scrape_queue


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


class QueueView(TemplateView):
    template_name = "scrapes/lists/queue.html"

    def get_context_data(self, **kwargs):
        context = {"queue": scrape_queue().prefetch_related('parser_type')}
        return context


class HistoryView(TemplateView):
    template_name = "scrapes/lists/history.html"


class TestView(TemplateView):
    template_name = "base.html"
