from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProfileForm
from .models import User

from django.contrib.auth.views import LogoutView as LogoutViewBase


class LogoutView(LogoutViewBase):
    template_name = "profiles/logout.html"


class LoginView(TemplateView):
    template_name = "profiles/login.html"


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    model = User
    template_name = "profiles/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):

        return super().form_valid(form)
