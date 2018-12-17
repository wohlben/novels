from django.views.generic import TemplateView
from novels.models import Fiction


class WatchingListView(TemplateView):
    template_name = "novels/lists/novels.html"

    def get_context_data(self, **kwargs):
        print(self.request.user)
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


class SearchComponent(TemplateView):
    template_name = "novels/components/search.html"

    def get_context_data(self, **kwargs):
        context = {'novels': Fiction.objects.all().order_by('title').values('id', 'title')}
        return context
