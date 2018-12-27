from django.conf import settings
from django.urls import path
from novels import views
from . import APP_NAME
from django.views.decorators.cache import cache_page


app_name = APP_NAME

urlpatterns = [
    path("", views.FictionListView.as_view(), name="novels"),
    path("updates", views.ChaptersListView.as_view(), name="updates"),
    path("watch/<novel_id>", views.WatchComponent.as_view(), name="watch-component"),
    path("novel/<novel_id>", views.FictionDetailView.as_view(), name="novel"),
    path("chapter/<chapter_id>", views.ChapterDetailView.as_view(), name="chapter"),
    path(
        "search",
        cache_page(settings.GENERIC_CACHE_TIME, cache="pages")(views.SearchComponent.as_view()),
        name="search",
    ),
]
