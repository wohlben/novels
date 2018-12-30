from django.test import TestCase
from scrapes import models
from scrapes.managers import RRLLatestScraper
import logging

rrl_latest = RRLLatestScraper()


class FetchLatestTestCase(TestCase):
    rrl_latest_parser_id = int

    @classmethod
    def setUpTestData(cls):
        logging.disable(logging.CRITICAL)
        cls.rrl_latest_parser_id = models.Parser.objects.get(name="rrl latest").id

    def pending_fetches(self):
        return rrl_latest._pending_fetches()

    def last_fetch(self):
        return rrl_latest._last_fetch()

    def add_queue_event(self):
        return rrl_latest.add_queue_event()

    def scrape_queue(self):
        return rrl_latest.scrape_queue()

    def test_starting_data(self):
        pending_fetches = self.pending_fetches()
        self.assertEqual(
            pending_fetches, 0, f"{pending_fetches} unexpected pending parses found"
        )

    def test_fetch_latest_add_to_queue(self):
        self.add_queue_event()
        pending_fetches = self.pending_fetches()
        self.assertEqual(
            pending_fetches, 1, f"found {pending_fetches} in the queue, expected one"
        )

    def test_fetch_latest_repeated_add(self):
        self.add_queue_event()
        self.add_queue_event()
        self.add_queue_event()

        pending_fetches = self.pending_fetches()
        self.assertEqual(
            pending_fetches,
            1,
            f"further calls shouldn't add another fetch to the queue, found {pending_fetches}",
        )

    def test_fetch_latest_recent_fetch(self):
        self.add_queue_event()

        last_fetch = self.last_fetch()
        last_fetch.content = "dummycontent"
        last_fetch.http_code = "200"
        last_fetch.save()

        self.add_queue_event()

        pending_fetches = self.pending_fetches()
        self.assertEqual(
            pending_fetches,
            0,
            f"recently fetched content shouldn't be enqueued again - found {pending_fetches}",
        )
