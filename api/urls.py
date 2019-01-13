from . import APP_NAME
from django.urls import path, include
from rest_framework import routers
from api.views import ChapterViewSet, FictionViewSet, ReadingProgressViewSet

app_name = APP_NAME

router = routers.DefaultRouter()
router.register(r"chapters", ChapterViewSet)
router.register(r"novels", FictionViewSet)
router.register(r"progress", ReadingProgressViewSet, "progress-detail")

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
