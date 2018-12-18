from django.views.generic import TemplateView, FormView
from novels.models import Fiction, Chapter
from novels.forms import WatchingForm
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

class WatchComponent(TemplateView):
    template_name = "novels/components/watch.html"

    def get_context_data(self, novel_id, **kwargs):
        # dependency: font-awesome
        context = {'novel': Fiction.objects.get(id=novel_id), 'icon': 'fa-eye'}
        if self.request.user.fiction_set.filter(id=novel_id).count() > 0:
            context['icon'] = 'fa-eye-slash'
        return context

class ToggleFictionWatch(FormView):
    form_class = WatchingForm
    template_name = "generic_form.html"

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            novel_id = request.POST.get('novel_id')
            fiction = Fiction.objects.get(id=novel_id)
            if request.user.fiction_set.filter(id=fiction.id).count() > 0:
                fiction.watching.remove(request.user)
            else:
                fiction.watching.add(request.user)
        return HttpResponseRedirect(reverse_lazy("novels:watch-component", kwargs={'novel_id':fiction.id}))

class WatchingListView(TemplateView):
    template_name = "novels/lists/novels.html"

    def get_context_data(self, **kwargs):
        context = {'novels': self.request.user.watching.values('id', 'title', 'author',)}
        return context

class FictionListView(TemplateView):
    template_name = "novels/lists/novels.html"

    def get_context_data(self, **kwargs):
        context = {'novels': Fiction.objects.all().order_by('title').values('id', 'title', 'author',)}
        return context


class FictionDetailView(TemplateView):
    template_name = "novels/details/novel.html"

    def get_context_data(self, novel_id):
        context = {'novel': Fiction.objects.get(id=novel_id)}
        return context

class ChapterDetailView(TemplateView):
    template_name = "novels/details/chapter.html"

    def get_context_data(self, chapter_id):
        context = {'chapter': Chapter.objects.prefetch_related('fiction').get(id=chapter_id)}
        return context

class SearchComponent(TemplateView):
    template_name = "novels/components/search.html"

    def get_context_data(self, **kwargs):
        context = {'novels': Fiction.objects.all().order_by('title').values('id', 'title')}
        return context
