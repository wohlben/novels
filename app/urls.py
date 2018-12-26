"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.views.generic.base import RedirectView
from profiles.views import LoginView, ProfileView, LogoutView
from django.conf import settings

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="scrapes:home", permanent=False)),
    path("novels/", include("novels.urls")),
    path("scrapes/", include("scrapes.urls")),
    path("api/", include("api.urls", namespace="api")),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile", ProfileView.as_view(), name="profile"),
    path("auth/", include("social_django.urls", namespace="social")),
    path("api-auth/", include("rest_framework.urls")),
]

if settings.DEBUG:  # pragma: no cover
    print("importing debug toolbar")
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
