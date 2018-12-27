from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin as __LoginRequiredMixin
from .forms import ProfileForm, BulkWatchForm
from .models import User as User, BulkWatchJob, ProvidedUrl
from scrapes.models import Parser, Scrapes
from novels.models import Fiction
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
import re

from django.contrib.auth.views import (
    LogoutView as LogoutViewBase,
    LoginView as LoginViewBase,
)
from django.core.cache import cache


class BulkWatchProgress(__LoginRequiredMixin, TemplateView):
    template_name = "profiles/details/bulk_watch_progress.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job"] = BulkWatchJob.objects.get(id=kwargs.get("job_id"))
        return context


class BulkWatchComponent(__LoginRequiredMixin, FormView):
    form_class = BulkWatchForm
    template_name = "profiles/components/bulk_watch.html"

    def form_valid(self, form):
        urls = form.data["url_list"].splitlines()
        print(f"working with {urls}")
        job = BulkWatchJob.objects.create(user=self.request.user)
        parsers = Parser.objects.all()
        for url in urls:
            provided_url = ProvidedUrl.objects.create(job=job, url=url)
            try:
                existing_fiction = Fiction.objects.filter(url=url)
                if existing_fiction.count() == 1:
                    provided_url.fiction = existing_fiction.first()
                    provided_url.fiction.watching.add(self.request.user)
                    provided_url.success = True
                    provided_url.save()
                    continue

                for parser in parsers:
                    if re.compile(parser.url_scheme).match(url):
                        provided_url.parser = parser
                        provided_url.save()

                if provided_url.parser:

                    if Scrapes.objects.filter(url=url).count() == 0:
                        scrape = Scrapes.objects.create(
                            url=url, parser_type=provided_url.parser
                        )
                    provided_url.scrape = scrape
                    provided_url.success = True
                    provided_url.save()
                    continue

                provided_url.success = False
                provided_url.save()

            except Exception as e:
                provided_url.success = False
                provided_url.save()
                print(f"failed to process {url}")
                raise

        return HttpResponseRedirect(
            reverse_lazy("profiles:bulk-watch-progress", kwargs={"job_id": job.id})
        )


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


class ProfileView(__LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    model = User
    template_name = "profiles/profile.html"
    success_url = reverse_lazy("profiles:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):

        return super().form_valid(form)
