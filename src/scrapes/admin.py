from django.contrib import admin
from .models import *


class ScrapesAdmin(admin.ModelAdmin):
    list_display = ["url", "timestamp"]


class ParserAdmin(admin.ModelAdmin):
    list_display = ["name", "added"]


admin.site.register(Parser, ParserAdmin)
admin.site.register(Scrapes, ScrapesAdmin)
