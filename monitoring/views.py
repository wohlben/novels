from django.views.generic import TemplateView as _TemplateView
from django.contrib.auth.mixins import (
    PermissionRequiredMixin as _PermissionRequiredMixin,
)
from profiles.models import ProvidedUrl as _ProvidedUrls
from scrapes.models import Scrapes as _Scrapes, ParseLog as _Parselog
from novels.models import Fiction as _Fiction, Chapter as _Chapter

# Create your views here.


class MonitoringView(_PermissionRequiredMixin, _TemplateView):
    template_name = "monitoring/main.html"
    permission_required = "scrapes.view_system"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unresolved_provided_urls"] = _ProvidedUrls.objects.filter(
            fiction=None
        ).prefetch_related("scrape", "job__user")
        context["failed_fetches"] = _Scrapes.objects.filter(content=None).exclude(
            http_code=None
        )
        context["failed_parses"] = _Parselog.objects.exclude(success=True)
        context["sourceless_fictions"] = _Fiction.objects.filter(source=None)
        context["unprocessed_highlights"] = _Chapter.objects.exclude(content=None).filter(highlight=None).count()
        return context
