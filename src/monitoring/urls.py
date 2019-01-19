from django.urls import path as _path
from . import views


app_name = "monitoring"

urlpatterns = [_path("", views.MonitoringView.as_view(), name="monitoring")]
