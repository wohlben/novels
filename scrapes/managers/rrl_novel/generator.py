"""Conditionally creates pending fetches for new monitored novels ."""
from scrapes.models import Scrapes
from novels.models import Fiction


class RRLNovelGeneratorMixin(object):
    def pending_fetches(self):
        """Return Scrape urls of parser_type_id."""
        return Scrapes.objects.filter(parser_type_id=self.get_parser_id(), content=None)

    def missing_novels(self, *args, **kwargs):
        """Return monitored Fiction objects that should to be fetched."""
        qs = (
            Fiction.objects.exclude(watching=None)
            .exclude(url__in=self.pending_fetches().values("url"))
            .filter(author=None)
        )
        if kwargs.get("user"):
            qs.filter(watching=kwargs["user"])
        return qs

    def refetch_novel(self, novel_id):
        fic = Fiction.objects.get(id=novel_id)
        if self.pending_fetches().filter(url=fic.url).count() > 0:
            self.logger.info(f"{fic.title} is already queued, skipping")
            return False
        else:
            self.logger.info(f"added {fic.title} to the queue")
            Scrapes.objects.create(url=fic.url, parser_type_id=self.get_parser_id())
            return True

    def add_queue_events(self, *args, **kwargs):
        """Conditionally add a new pending fetch."""
        try:
            for novel in self.missing_novels(*args, **kwargs):
                self.logger.info(f"adding '{novel.title}' to the pending fetches")
                Scrapes.objects.create(
                    url=novel.url, parser_type_id=self.get_parser_id()
                )

            return True
        except Exception:  # pragma: no cover
            self.logger.exception(f"failed to add a novel to scraping queue")
