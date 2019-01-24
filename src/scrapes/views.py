from django.views.generic import TemplateView as _TemplateView, FormView as _FormView
from scrapes.models import ParseLog as _ParseLog
from django.db.models import Count as _Count, F as _F
from scrapes.managers import Managers as _Managers
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
