from django.conf import settings as _settings
from django.urls import path as _path
from novels import views as _views
from . import APP_NAME
from django.views.decorators.cache import cache_page as _cache_page


app_name = APP_NAME

urlpatterns = [
    _path("", _views.FictionListView.as_view(), name="novels"),
    _path("updates", _views.ChaptersListView.as_view(), name="updates"),
    _path("updates/novels", _views.UpdatedFictionListView.as_view(), name="updated-novels"),
    _path("watch/<novel_id>", _views.WatchComponent.as_view(), name="watch-component"),
    _path("novel/<novel_id>", _views.FictionDetailView.as_view(), name="novel"),
    _path("chapter/<chapter_id>", _views.ChapterDetailView.as_view(), name="chapter"),
    _path(
        "search",
        _cache_page(_settings.GENERIC_CACHE_TIME, cache="pages")(
            _views.SearchComponent.as_view()
        ),
        name="search",
    ),
]
