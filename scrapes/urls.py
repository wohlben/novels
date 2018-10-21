from django.urls import path
from scrapes import views
from . import APP_NAME

app_name = APP_NAME

urlpatterns = [
    path("", views.TestView.as_view(), name="home")
]
