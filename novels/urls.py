from django.urls import path
from novels import views
from . import APP_NAME

app_name = APP_NAME

urlpatterns = [
    path("", views.FictionListView.as_view(), name="novels"),
    path("watching", views.WatchingListView.as_view(), name="watching"),
    path("watch", views.ToggleFictionWatch.as_view(), name="watch"),
    path("watch/<novel_id>", views.WatchComponent.as_view(), name="watch-component"),
    path("novel/<novel_id>", views.FictionDetailView.as_view(), name="novel"),
    path("chapter/<chapter_id>", views.ChapterDetailView.as_view(), name="chapter"),
    path("search", views.SearchComponent.as_view(), name="search"),
]
