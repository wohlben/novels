from django.test import TestCase
from scrapes import models
from scrapes.managers import rrl_latest
from novels import models as novel_models
import logging


class ParseLatestTestCase(TestCase):
    fixtures = ["2018_10_14_scrapes.json"]
    parser_id = int

    @classmethod
    def setUpTestData(cls):
        logging.disable(logging.CRITICAL)
        cls.parser_id = models.Parser.objects.get(name="rrl latest").id

    def pending_parses(self):
        return rrl_latest.all_pending_parses().count()

    @staticmethod
    def available_scrapes():
        return models.Scrapes.objects.all().count()

    @staticmethod
    def available_fictions():
        return novel_models.Fiction.objects.all().count()

    @staticmethod
    def available_chapters():
        return novel_models.Chapter.objects.all().count()

    def latest_extractor(self):
        return rrl_latest.latest_extractor()

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
        self.latest_extractor()
        pending_parses = self.pending_parses()
        self.assertEqual(0, pending_parses, f"found {pending_parses}, after parsing")

    def test_repeated_parses_executions(self):
        self.latest_extractor()
        self.latest_extractor()
        pending_parses = self.pending_parses()
        self.assertEqual(0, pending_parses, f"found {pending_parses}, after parsing")

    def test_parsed_fictions(self):
        self.latest_extractor()
        novels = novel_models.Fiction.objects.all().count()
        self.assertGreater(novels, 0, msg="the Parser should've created some novels...")

    def test_parsed_chapters(self):
        self.latest_extractor()
        chapters = novel_models.Chapter.objects.all().count()
        self.assertGreater(
            chapters, 0, msg="the Parser should've created some chapters..."
        )
