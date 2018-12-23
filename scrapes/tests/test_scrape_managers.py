from django.test import TestCase
from scrapes.managers import Managers
from novels.models import Fiction, Chapter


class ScrapeManagersTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        self.managers = Managers()

        fictions = [
            {"title": "monitored", "url": "someurl/fiction/1/novelname"},
            {"title": "unmonitored", "url": "another-url/fiction/22/novel-name2"},
        ]
        self.fics = [Fiction.objects.create(**fic) for fic in fictions]
        chapters = [
            {"fiction": self.fics[0], "url": "someurl/chapter/333/chapter"},
            {
                "fiction": self.fics[0],
                "url": "someurl/chapter/334/chapter",
                "content": "blub",
            },
            {"fiction": self.fics[1], "url": "someurl/chapter/3/chapter"},
            {"fiction": self.fics[1], "url": "someurl/chapter/4/chapter"},
        ]
        self.chaps = [Chapter.objects.create(**chap) for chap in chapters]

    def test_starting_data(self):
        self.assertEqual(
            self.managers.manager.scrape_queue().count(),
            0,
            "The scrape queue is expected to be empty",
        )

    def test_scrape_queue_contents(self):
        self.managers.rrl_chapter.refetch_chapter(self.chaps[0].id)
        self.managers.rrl_latest.add_queue_event()
        self.managers.rrl_novel.refetch_novel(self.fics[0].id)
        scrape_queue = self.managers.manager.scrape_queue()
        self.assertEqual(
            scrape_queue.count(),
            3,
            f"There should be three queued fetches, found {scrape_queue}",
        )

    def test_scrape_queue_order(self):
        self.managers.rrl_chapter.refetch_chapter(self.chaps[0].id)
        self.managers.rrl_latest.add_queue_event()
        self.managers.rrl_novel.refetch_novel(self.fics[0].id)
        scrape_queue = self.managers.manager.scrape_queue()
        self.assertEqual(scrape_queue[0].parser_type.name, "rrl latest")
        self.assertEqual(scrape_queue[1].parser_type.name, "rrl novel")
        self.assertEqual(scrape_queue[2].parser_type.name, "rrl chapter")
