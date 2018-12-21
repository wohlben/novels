from django.urls import path
from scrapes import views
from . import APP_NAME

app_name = APP_NAME

urlpatterns = [
    path("", views.TestView.as_view(), name="home"),
    path("history", views.HistoryView.as_view(), name="history"),
    path("queue", views.QueueView.as_view(), name="queue"),
    path("log", views.ParseLogListView.as_view(), name="log"),
    path(
        "requeue/chapter/<int:chapter_id>",
        views.RequeueChapterComponent.as_view(),
        name="requeue-chapter",
    ),
    path(
        "requeue/novel/<int:novel_id>",
        views.RequeueNovelComponent.as_view(),
        name="requeue-novel",
    ),
]
