from django.urls import path
from scrapes import views
from . import APP_NAME

app_name = APP_NAME

urlpatterns = [
    path("history", views.HistoryView.as_view(), name="history"),
    path("queue", views.QueueView.as_view(), name="queue"),
    path("log", views.ParseLogListView.as_view(), name="log"),
]
