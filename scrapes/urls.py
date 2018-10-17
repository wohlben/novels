from django.urls import path
from scrapes import views


urlpatterns = [
    path('', views.TestView.as_view())
]
