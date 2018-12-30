from django.urls import path
from profiles import views


app_name = "profiles"

urlpatterns = [
    path("", views.ProfileView.as_view(), name="profile"),
    path(
        "progress/<int:chapter_id>/<int:progress>",
        views.ReadingProgressView.as_view(),
        name="reading-progress",
    ),
    path("bulk-watch", views.BulkWatchComponent.as_view(), name="bulk-watch-component"),
    path(
        "bulk-watch-progress/<job_id>",
        views.BulkWatchProgress.as_view(),
        name="bulk-watch-progress",
    ),
]
