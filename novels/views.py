from django.views.generic import TemplateView, FormView
from django.db.models import Prefetch
from scrapes.models import Parser, Scrapes
from novels.models import Fiction, Chapter
from novels.forms import WatchingForm
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .filters import FictionFilter, ChapterFilter
from scrapes.managers import RRLNovelScraper
import re as __re

rrl_novel = RRLNovelScraper()


class WatchComponent(LoginRequiredMixin, FormView):
    form_class = WatchingForm
    template_name = "novels/components/watch.html"

    def get_context_data(self):
        novel_id = self.kwargs.get("novel_id")
        context = {"novel": Fiction.objects.get(id=novel_id), "watching": False}
        if self.request.user.fiction_set.filter(id=novel_id).count() > 0:
            context["watching"] = True
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            novel_id = kwargs.get("novel_id")
            fiction = Fiction.objects.get(id=novel_id)
            if request.user.fiction_set.filter(id=fiction.id).count() == 0:
                fiction.watching.add(request.user)
            else:
                fiction.watching.remove(request.user)
        rrl_novel.add_queue_events(user=request.user)
        return HttpResponseRedirect(
            reverse_lazy("novels:watch-component", kwargs={"novel_id": fiction.id})
        )


class SearchComponent(TemplateView):
    template_name = "novels/components/search.html"

    def get_context_data(self, **kwargs):
        context = {
            "novels": Fiction.objects.all().order_by("title").values("id", "title")
        }
        if self.request.GET.get("ic-request") != "true":
            context["debug_search"] = True
        return context


class ChaptersListView(TemplateView):
    template_name = "novels/lists/chapters.html"

    def get_context_data(self, **kwargs):

        prefetch = Prefetch("fiction", queryset=Fiction.objects.only("title", "author"))
        qs = (
            Chapter.objects.order_by("-published")
            .prefetch_related(prefetch)
            .only("id", "title", "published", "fiction", "url", "discovered")
        )
        if self.request.user.is_authenticated and self.request.user.internal_links:
            qs = qs.exclude(published=None)
        chapters = ChapterFilter(
            {"user": self.request.user, **self.request.GET}, queryset=qs
        ).qs
        page = self.request.GET.get("page")
        paginator = Paginator(chapters, 50)
        chapters = paginator.get_page(page)
        return {"chapters": chapters}


class FictionListView(TemplateView):
    template_name = "novels/lists/novels.html"

    def get_context_data(self, **kwargs):
        qs = Fiction.objects.order_by("title").values("id", "title", "author")
        novels = FictionFilter(
            {"user": self.request.user, **self.request.GET}, queryset=qs
        ).qs
        page = self.request.GET.get("page")
        paginator = Paginator(novels, 50)
        novels = paginator.get_page(page)
        return {"novels": novels}


class FictionDetailView(TemplateView):
    template_name = "novels/details/novel.html"

    def get_context_data(self, novel_id):
        return {"novel": Fiction.objects.get(id=novel_id)}


class ChapterDetailView(TemplateView):
    template_name = "novels/details/chapter.html"

    def get_context_data(self, chapter_id):
        context = {
            "chapter": Chapter.objects.prefetch_related("fiction").get(id=chapter_id)
        }
        return context
