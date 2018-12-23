from django.views.generic import TemplateView, FormView
from novels.models import Fiction, Chapter
from novels.forms import WatchingForm
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect


class WatchComponent(FormView):
    form_class = WatchingForm
    template_name = "novels/components/watch.html"

    def get_context_data(self):
        novel_id = self.kwargs.get('novel_id')
        context = {"novel": Fiction.objects.get(id=novel_id), "watching": False}
        if self.request.user.fiction_set.filter(id=novel_id).count() > 0:
            context['watching'] = True
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

        return HttpResponseRedirect(
            reverse_lazy("novels:watch-component", kwargs={"novel_id": fiction.id})
        )


class SearchComponent(LoginRequiredMixin, TemplateView):
    template_name = "novels/components/search.html"

    def get_context_data(self, **kwargs):
        context = {
            "novels": Fiction.objects.all().order_by("title").values("id", "title")
        }
        return context


class FictionListView(TemplateView):
    template_name = "novels/lists/novels.html"

    def get_context_data(self, **kwargs):
        context = {}
        if self.request.GET.get("populated"):
            context["novels"] = (
                Fiction.objects.order_by("title")
                .filter(id__in=Chapter.objects.exclude(content=None).values("fiction"))
                .values("id", "title", "author")
            )
        elif self.request.GET.get("watching"):
            context["novels"] = self.request.user.watching.values(
                "id", "title", "author"
            )
        else:
            context["novels"] = (
                Fiction.objects.all().order_by("title").values("id", "title", "author")
            )

        return context


class FictionDetailView(TemplateView):
    template_name = "novels/details/novel.html"

    def get_context_data(self, novel_id):
        context = {"novel": Fiction.objects.get(id=novel_id)}
        return context


class ChapterDetailView(TemplateView):
    template_name = "novels/details/chapter.html"

    def get_context_data(self, chapter_id):
        context = {
            "chapter": Chapter.objects.prefetch_related("fiction").get(id=chapter_id)
        }
        return context


class SearchComponent(TemplateView):
    template_name = "novels/components/search.html"

    def get_context_data(self, **kwargs):
        context = {
            "novels": Fiction.objects.all().order_by("title").values("id", "title")
        }
        return context
