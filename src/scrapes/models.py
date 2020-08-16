"""Database definitions for the Scrapes app."""
from django.db import models as _models


class Scrapes(_models.Model):
    """Urls that should be Scraped."""

    class Meta:
        permissions = (
            ("force_fetch", "Allows a User to force a fetch from the source"),
            ("view_system", "Allows the User to see the System views"),
        )

    url = _models.TextField(blank=False)
    timestamp = _models.DateTimeField(auto_now_add=True)
    last_change = _models.DateTimeField(auto_now=True)
    content = _models.TextField(blank=True, null=True)
    http_code = _models.IntegerField(blank=True, null=True)
    parser_type = _models.ForeignKey("Parser", on_delete=_models.CASCADE)
    added_by = _models.ForeignKey(
        "ParseLog", null=True, blank=True, related_name="added_by", on_delete=_models.SET_NULL,
    )
    added_reason = _models.TextField(blank=True, null=True)


class Parser(_models.Model):
    """Category of Scrapes and which parser should be applied."""

    name = _models.TextField()
    added = _models.DateTimeField(auto_now_add=True)
    url_scheme = _models.TextField(blank=True)
    weight = _models.IntegerField(default=50)

    @property
    def pending(self):
        return Scrapes.objects.filter(parser_type=self, http_code=None)


class ParseLog(_models.Model):
    """Log of all Parses."""

    scrape = _models.ForeignKey("Scrapes", on_delete=_models.CASCADE)
    parser = _models.ForeignKey("Parser", on_delete=_models.CASCADE)
    started = _models.DateTimeField(blank=True, null=True)
    finished = _models.DateTimeField(blank=True, null=True)
    success = _models.BooleanField(default=False)
    modified_object = _models.JSONField(blank=True, null=True)
