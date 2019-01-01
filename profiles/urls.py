from django.urls import path
from profiles import views


app_name = "profiles"

urlpatterns = [
    path("", views.ProfileView.as_view(), name="profile"),
    path(
        "progress/<int:chapter_id>/<progress>",
        views.ReadingProgressView.as_view(),
        name="reading-progress",
    ),
    path(
        "missed-progress/<int:chapter_id>",
        views.MissedReadingProgressAlertView.as_view(),
        name="bulk-reading-progress",
    ),
    path("bulk-watch", views.BulkWatchComponent.as_view(), name="bulk-watch-component"),
    path(
        "bulk-watch-progress/<job_id>",
        views.BulkWatchProgress.as_view(),
        name="bulk-watch-progress",
    ),
]
