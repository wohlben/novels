from django.test import TestCase
from scrapes import models
from scrapes.managers import rrl_novel
from novels import models as novel_models
from profiles.models import User
import logging


class ParseNovelTestCase(TestCase):
    fixtures = ["2018-10-17.json"]
    parser_id = int

    @classmethod
    def setUpTestData(cls):
        logging.disable(logging.CRITICAL)
        cls.parser_id = models.Parser.objects.get(name="rrl novel").id
        user = User.objects.create(username="testuser")
        novel_models.Fiction.objects.all()[0].watching.add(user)

    def pending_parses(self):
        return rrl_novel.all_pending_parses().count()

    def available_scrapes(self):
        return models.Scrapes.objects.filter(parser_type_id=self.parser_id).count()

    @staticmethod
    def available_chapters():
        return novel_models.Chapter.objects.all().count()

    def novel_extractor(self):
        return rrl_novel.novel_extractor()

    def test_fixture_data_pending_parses(self):
        pending_parses = self.pending_parses()
        self.assertGreater(
            pending_parses, 0, "test data doesn't provide any relevant data to parse"
        )

    def test_fixture_data_available_scrapes(self):
        available_scrapes = self.available_scrapes()
        self.assertGreater(
            available_scrapes,
            0,
            "testing data doesn't have any relevant scrapes. nothing can be done without data.",
        )

    def test_fixture_data_available_fictions(self):
        monitored = novel_models.Fiction.objects.exclude(watching=None).count()
        unmonitored = novel_models.Fiction.objects.filter(watching=None).count()
        self.assertGreater(
            monitored, 0, f"we'll need a monitored fiction for the tests"
        )
        self.assertGreater(
            unmonitored, 0, "while we don't strictly need one, i still want one..."
        )

    def test_pending_parses_execution(self):
        self.novel_extractor()
        pending_parses = self.pending_parses()
        self.assertEqual(0, pending_parses, f"found {pending_parses}, after parsing")

    def test_repeated_parses_executions(self):
        self.novel_extractor()
        self.novel_extractor()
        pending_parses = self.pending_parses()
        self.assertEqual(0, pending_parses, f"found {pending_parses}, after parsing")

    def test_parsed_chapters(self):
        self.novel_extractor()
        chapters = self.available_chapters()
        self.assertGreater(
            chapters, 0, msg="the Parser should've created some chapters..."
        )
