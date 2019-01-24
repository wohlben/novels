from django.apps import AppConfig


class ScrapesConfig(AppConfig):
    name = "scrapes"

    def ready(self):
        import scrapes.signals
