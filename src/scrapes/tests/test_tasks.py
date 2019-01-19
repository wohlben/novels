from django.test import TestCase
import logging
from scrapes import tasks


class TasksTestCase(TestCase):
    fixtures = ["2018_10_14_scrapes.json", "2018-10-17.json"]

    @classmethod
    def setUpTestData(cls):
        logging.disable(logging.CRITICAL)

    def test_generators(self):
        self.assertEquals(tasks.generators_task(), True)

    def test_parsers(self):
        self.assertEquals(tasks.parsers_task(), True)
