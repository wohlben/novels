from django.test import TestCase
from scrapes import tasks, models
from scrapes.parsers import rrl as rrl_parser
from scrapes.url_generators import rrl_latest as rrl_generator
from novels import models as novel_models
import logging


class FetchLatestTestCase(TestCase):
    rrl_latest_parser_id = int

    @classmethod
    def setUpTestData(cls):
        logging.disable(logging.CRITICAL)
        cls.rrl_latest_parser_id = models.Parser.objects.get(name="rrl latest").id

    def pending_fetches(self):
        return rrl_generator.all_pending_fetches(self.rrl_latest_parser_id)

    def last_fetch(self):
        return rrl_generator.last_fetch(self.rrl_latest_parser_id)

    def test_starting_data(self):
        pending_fetches = self.pending_fetches()
        self.assertEqual(
            pending_fetches, 0, f"{pending_fetches} unexpected pending parses found"
        )

    def test_fetch_latest_add_to_queue(self):
        tasks.fetch_latest()
        pending_fetches = self.pending_fetches()
        self.assertEqual(
            pending_fetches, 1, f"found {pending_fetches} in the queue, expected one"
        )

    def test_fetch_latest_repeated_add(self):
        tasks.fetch_latest()
        tasks.fetch_latest()
        tasks.fetch_latest()

        pending_fetches = self.pending_fetches()
        self.assertEqual(
            pending_fetches,
            1,
            f"further calls shouldn't add another fetch to the queue, found {pending_fetches}",
        )

    def test_fetch_latest_recent_fetch(self):
        tasks.fetch_latest()

        last_fetch = self.last_fetch()
        last_fetch.content = "dummycontent"
        last_fetch.http_code = "200"
        last_fetch.save()

        tasks.fetch_latest()

        pending_fetches = self.pending_fetches()
        self.assertEqual(
            pending_fetches,
            0,
            f"recently fetched content shouldn't be enqueued again - found {pending_fetches}",
        )


class ParseLatestTestCase(TestCase):
    fixtures = ["2018_10_14_scrapes.json"]
    parser_id = int

    @classmethod
    def setUpTestData(cls):
        logging.disable(logging.CRITICAL)
        cls.parser_id = models.Parser.objects.get(name="rrl latest").id

    def pending_parses(self):
        return rrl_parser.all_pending_parses(self.parser_id).count()

    @staticmethod
    def available_scrapes():
        return models.Scrapes.objects.all().count()

    @staticmethod
    def available_fictions():
        return novel_models.Fiction.objects.all().count()

    @staticmethod
    def available_chapters():
        return novel_models.Chapter.objects.all().count()

    def test_fixture_data_pending_parses(self):
        pending_parses = self.pending_parses()
        self.assertNotEquals(
            pending_parses,
            0,
            "didn't find any pending parses. maybe fixture wasn't imported?",
        )
        self.assertEquals(
            pending_parses,
            2,
            f"didn't find the expected amount of testing data -- found {pending_parses}",
        )

    def test_fixture_data_available_scrapes(self):
        available_scrapes = self.available_scrapes()
        self.assertEquals(
            available_scrapes,
            3,
            f"testing data should include 3 scrapes -- found {available_scrapes}",
        )

    def test_fixture_data_available_fictions(self):
        available_fictions = self.available_fictions()
        self.assertEqual(
            0,
            available_fictions,
            f"found {available_fictions} fictions after import, tests will be inconclusive",
        )

    def test_fixture_data_available_chapters(self):
        available_chapters = self.available_chapters()
        self.assertEqual(
            0,
            available_chapters,
            f"found {available_chapters} chapters after import, tests will be inconclusive",
        )

    def test_pending_parses_execution(self):
        tasks.parse_latest()
        pending_parses = self.pending_parses()
        self.assertEqual(0, pending_parses, f"found {pending_parses}, after parsing")

    def test_repeated_parses_executions(self):
        tasks.parse_latest()
        tasks.parse_latest()
        pending_parses = self.pending_parses()
        self.assertEqual(0, pending_parses, f"found {pending_parses}, after parsing")

    def test_parsed_fictions(self):
        tasks.parse_latest()
        novels = novel_models.Fiction.objects.all().count()
        self.assertGreater(novels, 0, msg="the Parser should've created some novels...")

    def test_parsed_chapters(self):
        tasks.parse_latest()
        chapters = novel_models.Chapter.objects.all().count()
        self.assertGreater(
            chapters, 0, msg="the Parser should've created some chapters..."
        )
