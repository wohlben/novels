from django.views.generic import TemplateView as _TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin as _PermissionRequiredMixin
from profiles.models import ProvidedUrl as _ProvidedUrls
from scrapes.models import Scrapes as _Scrapes, ParseLog as _Parselog, Parser as _Parser
from novels.models import Fiction as _Fiction, Chapter as _Chapter
from django.utils import timezone as _timezone
from datetime import timedelta as _timedelta
from django.db.models import Q as _Q, Count as _Count


class MonitoringView(_PermissionRequiredMixin, _TemplateView):
    template_name = "monitoring/main.html"
    permission_required = "scrapes.view_system"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unresolved_provided_urls"] = _ProvidedUrls.objects.filter(fiction=None).prefetch_related(
            "scrape", "job__user"
        )
        context["failed_fetches"] = _Scrapes.objects.filter(content=None).exclude(http_code=None)
        context["failed_parses"] = _Parselog.objects.exclude(success=True)
        context["total_scrapes"] = _Scrapes.objects.exclude(content=None).count()
        context["total_fetches"] = _Scrapes.objects.all().count()
        context["unparsed_scrapes"] = _Scrapes.objects.filter(parselog=None).exclude(content=None).count()
        context["scrape_queue"] = _Scrapes.objects.filter(http_code=None).count()
        context["sourceless_fictions"] = _Fiction.objects.filter(source=None)
        context["unprocessed_highlights"] = _Chapter.objects.exclude(content=None).filter(highlight=None).count()
        context["unprocessed_characters"] = _Chapter.objects.exclude(content=None).filter(characters=None).count()
        context["parsers"] = (
            _Parser.objects.all()
            .annotate(parses=_Count("parselog", filter=_Q(parselog__started__gt=_timezone.now() - _timedelta(days=2)),))
            .values("parses", "name", "id")
        )

        context["duplicates"] = (
            _Chapter.objects.exclude(remote_id=None)
            .values("remote_id")
            .annotate(ri_count=_Count("remote_id"))
            .filter(ri_count__gt=1)
            .count()
        )
        return context
