"""Conditionally creates pending fetches for unparsed chapters ."""
from scrapes.models import Scrapes
from novels.models import Chapter, Fiction
from datetime import timedelta
from django.utils import timezone


class RRLChapterGeneratorMixin(object):
    def pending_fetches(self):
        """Return Query Set of Scrapes within the last day."""
        return Scrapes.objects.filter(
            parser_type_id=self.parser_id,
            last_change__gt=timezone.now() - timedelta(days=1),
        ).values("url")


    def missing_chapters(self):
        """Return all chapters of monitored novels without content."""
        return Chapter.objects.filter(
            content=None, fiction__in=self.monitored_novels()
        ).exclude(url__in=self.pending_fetches())


    @staticmethod
    def monitored_novels():
        """Return IDs of all monitored Fiction objects."""
        return Fiction.objects.exclude(watching=None).values("id")


    def refetch_chapter(self, chapter_id):
        chapter = Chapter.objects.get(id=chapter_id)
        if chapter.url in self.pending_fetches():
            self.logger.info(f"{chapter.title} is already queued, skipping")
            return False
        else:
            Scrapes.objects.create(url=chapter.url, parser_type_id=self.parser_id)
            self.logger.info(f"added {chapter.title} to the queue")
            return True


    def add_queue_events(self):
        """Conditionally add a new pending fetch."""
        try:
            pending_chapters = self.missing_chapters()
            pending_chapters.select_related("fiction__monitored", "fiction__title")

            for chapter in pending_chapters:
                self.logger.info(
                    f"adding '{chapter.title}' chapter from '{chapter.fiction.title}' to the pending fetches"
                )
                Scrapes.objects.create(url=chapter.url, parser_type_id=self.parser_id)

            return True
        except Exception:  # pragma: no cover
            self.logger.exception('failed to add a new "rrl chapter" scrape')
