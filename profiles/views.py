from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProfileForm
from .models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

from django.contrib.auth.views import (
    LogoutView as LogoutViewBase,
    LoginView as LoginViewBase,
)
from django.core.cache import cache


class LogoutView(LogoutViewBase):
    template_name = "profiles/logout.html"


class LoginView(LoginViewBase):
    template_name = "profiles/login.html"

    def get(self, *args, **kwargs):
        login_token = self.request.GET.get("login_token")
        if login_token:
            user = authenticate(login_token)
            if user:
                login(self.request, user)
                return redirect(reverse_lazy("home"))
        return super().get(*args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    model = User
    template_name = "profiles/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):

        return super().form_valid(form)
