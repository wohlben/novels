"""Modeldefinitions for the novel app."""
from django.shortcuts import reverse
from django.db import models


class Fiction(models.Model):
    """Fiction database model."""

    pic_url = models.TextField(blank=True, null=True)
    pic = models.BinaryField(blank=True, null=True)
    title = models.TextField(blank=True)
    url = models.TextField()
    remote_id = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)

    watching = models.ManyToManyField("profiles.User")

    source = models.ForeignKey(
        "scrapes.Parser", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return self.title

    @property
    def get_absolute_url(self):
        return reverse("novels:novel", kwargs={"novel_id": self.pk})


class Chapter(models.Model):
    """Chapter database model."""

    class Meta:
        ordering = ["published", "id"]

    fiction = models.ForeignKey("Fiction", on_delete=models.CASCADE)
    title = models.TextField(blank=True, null=True)
    remote_id = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    published = models.DateTimeField(blank=True, null=True)
    published_relative = models.TextField(blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    discovered = models.DateTimeField(auto_now_add=True)
    url = models.TextField()
