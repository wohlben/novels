from django.test import TestCase
from scrapes.models import Parser
from novels.models import Fiction
from scrapes.fetch_generators import rrl_novel_generator
import logging


class GenerateNovelTestCase(TestCase):
    parser_id = int
    starting_missing_novels = int

    @classmethod
    def setUpTestData(cls):
        logging.disable(logging.CRITICAL)
        cls.parser_id = Parser.objects.get(name="rrl novel").id
        cls.starting_missing_novels = cls.missing_novels(cls)

    def setUp(self):
        fictions = [
            {
                "title": "monitored",
                "monitored": True,
                "url": "someurl/fiction/1/novelname",
            },
            {
                "title": "monitored",
                "monitored": True,
                "url": "someurl/fiction/1/novelname",
                "author": "some-author",
            },
            {
                "title": "unmonitored",
                "monitored": False,
                "url": "another-url/fiction/22/novel-name2",
            },
            {
                "title": "unmonitored",
                "monitored": False,
                "url": "another-url/fiction/22/novel-name2",
                "author": "some-author",
            },
        ]
        [Fiction.objects.create(**fic) for fic in fictions]

    def add_queue_events(self):
        return rrl_novel_generator.add_queue_events(self.parser_id)

    def missing_novels(self):
        return rrl_novel_generator.missing_novels(self.parser_id).count()

    def pending_fetches(self):
        return len(rrl_novel_generator.pending_fetches(self.parser_id))

    def test_starting_data(self):
        self.assertGreater(
            self.missing_novels(),
            0,
            "test data isn't providing anything to add to the pending queue",
        )

    def test_adding_fetch_events(self):
        self.add_queue_events()
        self.assertEquals(
            self.missing_novels(), 0, "we're still finding chapters to queue..."
        )

    def test_correct_amount_added(self):
        pending = self.pending_fetches()
        self.add_queue_events()
        self.assertEquals(pending + 1, self.pending_fetches())
