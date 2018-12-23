from django.test import TestCase
from scrapes.models import Parser
from novels.models import Fiction, Chapter
from profiles.models import User
from scrapes.managers import RRLChapterScraper
import logging

rrl_chapter = RRLChapterScraper()

class GenerateChapterTestCase(TestCase):
    parser_id = int

    @classmethod
    def setUpTestData(cls):
        logging.disable(logging.CRITICAL)
        cls.parser_id = Parser.objects.get(name="rrl chapter").id

    def setUp(self):
        fictions = [
            {"title": "monitored", "url": "someurl/fiction/1/novelname"},
            {"title": "unmonitored", "url": "another-url/fiction/22/novel-name2"},
        ]
        fics = [Fiction.objects.create(**fic) for fic in fictions]
        user = User.objects.create(username="testuser")
        fics[0].watching.add(user)
        chapters = [
            {"fiction": fics[0], "url": "someurl/chapter/333/chapter"},
            {
                "fiction": fics[0],
                "url": "someurl/chapter/334/chapter",
                "content": "blub",
            },
            {"fiction": fics[1], "url": "someurl/chapter/3/chapter"},
            {"fiction": fics[1], "url": "someurl/chapter/4/chapter"},
        ]
        self.chaps = [Chapter.objects.create(**chap) for chap in chapters]

    def add_queue_events(self):
        return rrl_chapter.add_queue_events()

    def monitored_novels(self):
        return len(rrl_chapter.monitored_novels())

    def missing_chapters(self):
        return rrl_chapter.missing_chapters().count()

    def pending_fetches(self):
        return rrl_chapter.pending_fetches().count()

    def refetch_chapter(self, chapter_id):
        return rrl_chapter.refetch_chapter(chapter_id)

    def test_starting_data(self):
        self.assertGreater(
            self.monitored_novels(), 0, "test data doesn't include any monitored novels"
        )
        self.assertGreater(
            self.missing_chapters(),
            0,
            "test data isn't providing anything to add to the pending queue",
        )

    def test_adding_fetch_events(self):
        self.add_queue_events()
        self.assertEquals(
            self.missing_chapters(), 0, "we're still finding chapters to queue..."
        )

    def test_correct_amount_added(self):
        pending = self.pending_fetches()
        self.add_queue_events()
        self.assertEquals(pending + 1, self.pending_fetches())

    def test_requeue_chapter(self):
        pending_fetches = self.pending_fetches()
        self.refetch_chapter(self.chaps[0].id)
        self.assertEqual(pending_fetches + 1, self.pending_fetches())

    def test_skip_requeue_if_already_queued(self):
        pending_fetches = self.pending_fetches()
        self.refetch_chapter(self.chaps[1].id)
        self.refetch_chapter(self.chaps[1].id)
        self.assertEqual(pending_fetches + 1, self.pending_fetches())
