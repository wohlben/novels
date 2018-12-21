from django.test import TestCase
from scrapes import models
from scrapes.managers import rrl_chapter
from novels import models as novel_models
import logging


class ParseChapterTestCase(TestCase):
    fixtures = ["2018-10-17.json"]
    parser_id = int

    @classmethod
    def setUpTestData(cls):
        logging.disable(logging.CRITICAL)
        cls.parser_id = models.Parser.objects.get(name="rrl chapter").id

    def pending_parses(self):
        return rrl_chapter.all_pending_parses().count()

    def available_scrapes(self):
        return models.Scrapes.objects.filter(parser_type_id=self.parser_id).count()

    @staticmethod
    def available_fictions():
        return novel_models.Fiction.objects.all().count()

    @staticmethod
    def available_chapters():
        return novel_models.Chapter.objects.all().count()

    def chapter_extractor(self):
        return rrl_chapter.chapter_extractor()

    def test_fixture_data_pending_parses(self):
        pending_parses = self.pending_parses()
        self.assertGreater(
            pending_parses, 0, "test data doesn't provide any data to parse"
        )

    def test_fixture_data_available_scrapes(self):
        available_scrapes = self.available_scrapes()
        self.assertGreater(
            available_scrapes,
            0,
            "testing data doesn't have any scrapes. nothing can be done without data.",
        )

    def test_fixture_data_available_fictions(self):
        available_fictions = self.available_fictions()
        self.assertGreater(
            available_fictions,
            1,
            f"we'll need *at least* two fictions for testing, one monitored",
        )

    def test_fixture_data_available_chapters(self):
        available_chapters = self.available_chapters()
        self.assertGreater(
            available_chapters,
            0,
            f"we'll need at least one chapter to append the content of the test",
        )

    def test_pending_parses_execution(self):
        self.chapter_extractor()
        pending_parses = self.pending_parses()
        self.assertEqual(0, pending_parses, f"found {pending_parses}, after parsing")

    def test_repeated_parses_executions(self):
        self.chapter_extractor()
        self.chapter_extractor()
        pending_parses = self.pending_parses()
        self.assertEqual(0, pending_parses, f"found {pending_parses}, after parsing")

    def test_parsed_fictions(self):
        self.chapter_extractor()
        novels = novel_models.Fiction.objects.all().count()
        self.assertGreater(novels, 0, msg="the Parser should've created some novels...")

    def test_parsed_chapters(self):
        self.chapter_extractor()
        chapters = novel_models.Chapter.objects.all().count()
        self.assertGreater(
            chapters, 0, msg="the Parser should've created some chapters..."
        )
