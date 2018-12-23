from django.test import TestCase
from scrapes.models import Parser
from novels.models import Fiction
from profiles.models import User
from scrapes.managers import RRLNovelScraper

rrl_novel = RRLNovelScraper()


class GenerateNovelTestCase(TestCase):
    parser_id = int
    starting_missing_novels = int

    @classmethod
    def setUpTestData(cls):
        cls.parser_id = Parser.objects.get(name="rrl novel").id
        cls.starting_missing_novels = cls.missing_novels(cls)

    def setUp(self):
        fictions = [
            {"title": "monitored", "url": "someurl/fiction/1/novelname"},
            {
                "title": "monitored",
                "url": "someurl/fiction/1/novelname",
                "author": "some-author",
            },
            {"title": "unmonitored", "url": "another-url/fiction/22/novel-name2"},
            {
                "title": "unmonitored",
                "url": "another-url/fiction/22/novel-name2",
                "author": "some-author",
            },
        ]
        self.fics = [Fiction.objects.create(**fic) for fic in fictions]
        user = User.objects.create(username="testuser")
        self.fics[0].watching.add(user)
        self.fics[1].watching.add(user)

    def add_queue_events(self):
        return rrl_novel.add_queue_events()

    def missing_novels(self):
        return rrl_novel.missing_novels().count()

    def pending_fetches(self):
        return len(rrl_novel.pending_fetches())

    def refetch_novel(self, novel_id):
        return rrl_novel.refetch_novel(novel_id)

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

    def test_requeue_novel(self):
        pending_fetches = self.pending_fetches()
        self.refetch_novel(self.fics[1].id)
        self.assertEqual(pending_fetches + 1, self.pending_fetches())

    def test_skip_requeue_if_queued(self):
        pending_fetches = self.pending_fetches()
        self.refetch_novel(self.fics[1].id)
        self.refetch_novel(self.fics[1].id)
        self.assertEqual(pending_fetches + 1, self.pending_fetches())


    def test_queue_only_fictions_without_authors(self):
        # the others should already be fetched after all
        pending = self.pending_fetches()
        self.add_queue_events()
        self.assertEquals(
            pending + 1,
            self.pending_fetches(),
            "test data should've added only one new fetch",
        )
