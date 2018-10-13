from django.db import models


class Scrapes(models.Model):
    url = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)
    content = models.TextField(blank=True, null=True)
    http_code = models.IntegerField(blank=True, null=True)
    parser_type = models.ForeignKey("Parser", on_delete=models.CASCADE)


class Parser(models.Model):
    name = models.TextField()
    added = models.DateTimeField(auto_now_add=True)


class ParseLog(models.Model):
    scrape = models.ForeignKey("Scrapes", on_delete=models.CASCADE)
    parser = models.ForeignKey("Parser", on_delete=models.CASCADE)
    started = models.DateTimeField(blank=True, null=True)
    finished = models.DateTimeField(blank=True, null=True)
    success = models.BooleanField(default=False)
