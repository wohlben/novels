from django.http import (
    HttpResponseRedirect as _HttpResponseRedirect,
    HttpResponse as _HttpResponse,
)
from django.urls import reverse_lazy as _reverse_lazy, reverse as _reverse
from django.views.generic import (
    TemplateView as _TemplateView,
    UpdateView as _UpdateView,
    FormView as _FormView,
)
from django.contrib.auth.mixins import LoginRequiredMixin as _LoginRequiredMixin
from .forms import (
    ProfileForm as _ProfileForm,
    BulkWatchForm as _BulkWatchForm,
    ReadingProgressForm as _ReadingProgressForm,
    BulkReadingProgressForm as _BulkReadingProgressForm,
)
from .models import (
    User as _User,
    BulkWatchJob as _BulkWatchJob,
    ProvidedUrl as _ProvidedUrl,
    ReadingProgress as _ReadingProgress,
)
from scrapes.models import Parser as _Parser, Scrapes as _Scrapes
from novels.models import Fiction as _Fiction, Chapter as _Chapter
from django.contrib.auth import authenticate as _authenticate, login as _login
from django.shortcuts import redirect as _redirect
import re as _re

from django.contrib.auth.views import (
    LogoutView as _LogoutViewBase,
    LoginView as _LoginViewBase,
)


class MissedReadingProgressAlertView(_LoginRequiredMixin, _FormView):
    template_name = "profiles/components/missed_reading_progress_alert.html"
    form_class = _BulkReadingProgressForm

    def get_context_data(self, **kwargs):
        chapter_id = int(self.request.resolver_match.kwargs.get("chapter_id"))
        chapter = _Chapter.objects.get(id=chapter_id)
        context = super().get_context_data(**kwargs)
        context["previous_unread_chapters"] = chapter.get_unread_previous_chapters(
            self.request.user.id
        )
        context["chapter"] = chapter
        if self.request.GET.get("show-all"):
            context["show_all"] = True
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _HttpResponse(status=403)

        chapter_id = kwargs.get("chapter_id")
        chapter = _Chapter.objects.get(id=chapter_id)
        for chapter in chapter.get_unread_previous_chapters(self.request.user.id):
            progress_obj, created = _ReadingProgress.objects.get_or_create(
                user=self.request.user,
                chapter=chapter,
                defaults={"progress": chapter.total_progress},
            )
            if not created:
                progress_obj.progress = chapter.total_progress
                progress_obj.save()

        return _HttpResponseRedirect(
            _reverse_lazy(
                "profiles:bulk-reading-progress", kwargs={"chapter_id": chapter.id}
            )
        )


class ReadingProgressView(_LoginRequiredMixin, _FormView):
    template_name = "profiles/components/reading_progress.html"
    form_class = _ReadingProgressForm

    def get_context_data(self, **kwargs):
        context = dict(
            **self.request.resolver_match.kwargs, **super().get_context_data(**kwargs)
        )
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                reading_progress = int(kwargs.get("progress"))
            except (ValueError, TypeError):
                reading_progress = 0

            chapter = _Chapter.objects.get(id=kwargs["chapter_id"])
            reading_progress = int(reading_progress / chapter.total_progress * 100)

            progress, created = _ReadingProgress.objects.get_or_create(
                user=request.user,
                chapter_id=kwargs["chapter_id"],
                defaults={"progress": reading_progress},
            )
            if not created:
                if reading_progress == 0:
                    progress.delete()
                elif progress.progress < reading_progress or progress.progress == 0:
                    progress.progress = reading_progress
                    progress.save()
            return _HttpResponse(status=204)
        return _HttpResponse(status=403)


class BulkWatchProgress(_LoginRequiredMixin, _TemplateView):
    template_name = "profiles/details/bulk_watch_progress.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job"] = _BulkWatchJob.objects.get(id=kwargs.get("job_id"))
        return context


class BulkWatchComponent(_LoginRequiredMixin, _FormView):
    form_class = _BulkWatchForm
    template_name = "profiles/components/bulk_watch.html"

    def form_valid(self, form):
        urls = form.data["url_list"].splitlines()
        print(f"working with {urls}")
        job = _BulkWatchJob.objects.create(user=self.request.user)
        parsers = _Parser.objects.all()
        for url in urls:
            provided_url = _ProvidedUrl.objects.create(job=job, url=url)
            try:
                existing_fiction = _Fiction.objects.filter(url=url)
                if existing_fiction.count() == 1:
                    provided_url.fiction = existing_fiction.first()
                    provided_url.fiction.watching.add(self.request.user)
                    provided_url.success = True
                    provided_url.save()
                    continue

                for parser in parsers:
                    if _re.compile(parser.url_scheme).match(url):
                        provided_url.parser = parser
                        provided_url.save()

                if provided_url.parser:

                    if _Scrapes.objects.filter(url=url).count() == 0:
                        scrape = _Scrapes.objects.create(
                            url=url, parser_type=provided_url.parser
                        )
                    provided_url.scrape = scrape
                    provided_url.save()
                    continue

                provided_url.success = False
                provided_url.save()

            except Exception as e:
                provided_url.success = False
                provided_url.save()
                print(f"failed to process {url}")
                raise

        return _HttpResponseRedirect(
            _reverse_lazy("profiles:bulk-watch-progress", kwargs={"job_id": job.id})
        )


class LogoutView(_LogoutViewBase):
    template_name = "profiles/logout.html"


class LoginView(_LoginViewBase):
    template_name = "profiles/login.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return _HttpResponseRedirect(_reverse("profiles:profile"))
        login_token = self.request.GET.get("login_token")
        if login_token:
            user = _authenticate(login_token)
            if user:
                _login(self.request, user)
                return _redirect(_reverse_lazy("home"))
        return super().get(*args, **kwargs)


class ProfileView(_LoginRequiredMixin, _UpdateView):
    form_class = _ProfileForm
    model = _User
    template_name = "profiles/details/profile.html"
    success_url = _reverse_lazy("profiles:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):

        return super().form_valid(form)
