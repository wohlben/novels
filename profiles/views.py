from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = "profiles/login.html"


class ProfileView(TemplateView):
    template_name = "profiles/profile.html"
