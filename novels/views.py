from django.views.generic import TemplateView as _TemplateView, FormView as _FormView
from django.db.models import Prefetch as _Prefetch
from novels.models import Fiction as _Fiction, Chapter as _Chapter
from novels.forms import WatchingForm as _WatchingForm
from django.core.paginator import Paginator as _Paginator
from django.urls import reverse_lazy as _reverse_lazy
from django.http import (
    HttpResponseRedirect as _HttpResponseRedirect,
    HttpResponse as _HttpResponse,
)
from .filters import FictionFilter as _FictionFilter, ChapterFilter as _ChapterFilter
from scrapes.managers import (
    RRLNovelScraper as __RRLNovelScraper,
    RRLChapterScraper as __RRLChapterScraper,
)

_rrl_novel = __RRLNovelScraper()
_rrl_chapter = __RRLChapterScraper()


class WatchComponent(_FormView):
    form_class = _WatchingForm
    template_name = "novels/components/watch.html"

    def get_context_data(self):
        novel_id = self.kwargs.get("novel_id")
        context = {"novel": _Fiction.objects.get(id=novel_id), "watching": False}
        user = self.request.user
        if user.is_authenticated and user.fiction_set.filter(id=novel_id).count() > 0:
            context["watching"] = True
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = self.form_class(request.POST)
            if form.is_valid():
                novel_id = kwargs.get("novel_id")
                fiction = _Fiction.objects.get(id=novel_id)
                if request.user.fiction_set.filter(id=fiction.id).count() == 0:
                    fiction.watching.add(request.user)
                else:
                    fiction.watching.remove(request.user)
                _rrl_novel.add_queue_events(user=request.user)
                return _HttpResponseRedirect(
                    _reverse_lazy(
                        "novels:watch-component", kwargs={"novel_id": fiction.id}
                    )
                )
        return _HttpResponse(status=403)


class SearchComponent(_TemplateView):
    template_name = "novels/components/search.html"

    def get_context_data(self, **kwargs):
        context = {
            "novels": _Fiction.objects.all().order_by("title").values("id", "title")
        }
        if self.request.GET.get("ic-request") != "true":
            context["debug_search"] = True
        return context


class ChaptersListView(_TemplateView):
    template_name = "novels/lists/chapters.html"

    def get_context_data(self, **kwargs):
        prefetch = _Prefetch(
            "fiction", queryset=_Fiction.objects.only("title", "author")
        )
        qs = (
            _Chapter.objects.date_sorted()
            .prefetch_related(prefetch)
            .only("id", "title", "published", "fiction", "url", "discovered")
        )
        chapters = _ChapterFilter(
            {"user": self.request.user, **self.request.GET}, queryset=qs
        ).qs
        page = self.request.GET.get("page")
        paginator = _Paginator(chapters, 50)
        chapters = paginator.get_page(page)
        return {"chapters": chapters}


class FictionListView(_TemplateView):
    template_name = "novels/lists/novels.html"

    def get_context_data(self, **kwargs):
        qs = _Fiction.objects.order_by("title").values("id", "title", "author")
        novels = _FictionFilter(
            {"user": self.request.user, **self.request.GET}, queryset=qs
        ).qs
        page = self.request.GET.get("page")
        paginator = _Paginator(novels, 50)
        novels = paginator.get_page(page)
        return {"novels": novels}


class FictionDetailView(_TemplateView):
    template_name = "novels/details/novel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prefetch_qs = _Chapter.objects.date_sorted()
        user = self.request.user
        if user.is_authenticated:
            prefetch = _Prefetch(
                "chapter_set", queryset=prefetch_qs.add_progress(self.request.user.id)
            )
        else:
            prefetch = _Prefetch("chapter_set", queryset=prefetch_qs)

        novel = _Fiction.objects.prefetch_related(prefetch).get(
            id=kwargs.get("novel_id")
        )

        context["novel"] = novel
        if user.is_authenticated:
            context["last_read_chapter"] = novel.get_last_read_chapter(user.id)
        return context


class ChapterDetailView(_TemplateView):
    template_name = "novels/details/chapter.html"

    def get_context_data(self, **kwargs):
        chapter_id = kwargs["chapter_id"]
        chapter = _Chapter.objects.prefetch_related("fiction").get(id=chapter_id)

        if (
            self.request.GET.get("force-fetch")
            and self.request.user.has_perm("scrapes.force_fetch")
            and chapter.content is None
        ):
            scrape = _rrl_chapter.fetch_chapter(chapter_id, "forced user refresh")
            _rrl_chapter.parse(scrape_id=scrape)
            chapter.refresh_from_db()

        context = {"chapter": chapter}

        if chapter.content is None:
            context["scrape_queue_count"] = _rrl_novel.scrape_queue().count()

        if self.request.user.is_authenticated:
            reading_progress = self.request.user.readingprogress_set.filter(
                chapter_id=chapter.id
            )
            if reading_progress.count() > 0:
                context["progress"] = reading_progress.first()
        return context
