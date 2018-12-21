"""Provides discovery of pending fetches and creates them conditionally."""
from scrapes.models import Scrapes
from datetime import timedelta
from django.utils import timezone

PARSER_TYPE = "rrl latest"


class RRLLatestGeneratorMixin(object):
    def pending_fetches(self):
        """Return quantity of pending fetches relating to this module."""
        return Scrapes.objects.filter(
            http_code=None, content=None, parser_type_id=self.parser_id
        ).count()

    def last_fetch(self):
        """Return the last fetch object for modifications."""
        return Scrapes.objects.filter(parser_type_id=self.parser_id).last()

    def add_queue_event(self):
        """Conditionally add a new pending fetch."""
        try:
            pending_scrapes = self.pending_fetches()

            if pending_scrapes > 0:
                self.logger.warning(
                    f'found {pending_scrapes} pending scrapes for "rrl latest" -- skipping queue'
                )
                return False

            last_scrape = self.last_fetch()

            if last_scrape and last_scrape.last_change > timezone.now() - timedelta(
                minutes=15
            ):
                self.logger.warning(
                    f"last scrape was within 15 minutes ({last_scrape.last_change}) -- skipping queue"
                )
                return False

            self.logger.info('adding new "rrl latest" to the scrape queue')

            Scrapes.objects.create(
                url="https://www.royalroad.com/fictions/latest-updates",
                parser_type_id=self.parser_id,
            )
            return True
        except Exception:  # pragma: no cover
            self.logger.exception('failed to add a new "rrl latest" scrape')
