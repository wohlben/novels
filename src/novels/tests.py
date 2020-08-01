from django.test import TestCase as _TestCase
from django.urls import reverse as _reverse
from profiles.models import User as _User, ReadingProgress as _ReadingProgress
from novels.models import Fiction as _Fiction, Chapter as _Chapter
from scrapes.models import Parser as _Parser
from django.contrib.auth.models import Permission as _Permission


class WatchComponentTests(_TestCase):
    def setUp(self):
        parser = _Parser.objects.get(name="rrl novel")
        self.fic = _Fiction.objects.create(title="test fiction", url="https://some.fq.dn/with/uri", source=parser)

    def test_unauthenticated_get(self):
        response = self.client.get(_reverse("novels:watch-component", kwargs={"novel_id": self.fic.id}))
        self.assertEqual(response.status_code, 200, "unauthenticated users should get an empty 200")

    def test_get_context(self):
        self.client.force_login(_User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(_reverse("novels:watch-component", kwargs={"novel_id": self.fic.id}))
        self.assertEquals(
            type(response.context["novel"]), _Fiction, "There should be a Fiction object in the context",
        )
        self.assertContains(response, "unchecked")  # the watching status should still be false
        self.assertNotEqual(response.context.get("watching"), None, "watching should be defined")
        self.assertEqual(response.status_code, 200)

    def test_add_watching(self):
        self.client.force_login(_User.objects.get_or_create(username="testuser")[0])
        response = self.client.post(
            _reverse("novels:watch-component", kwargs={"novel_id": self.fic.id}), {"watch": True},
        )
        updated_response = self.client.get(_reverse("novels:watch-component", kwargs={"novel_id": self.fic.id}))
        self.assertContains(updated_response, "checked")  # the watching status should be true now
        self.assertEqual(response.status_code, 302, "The update should return with a redirect")
        self.assertEqual(updated_response.status_code, 200)

    def test_remove_watching(self):
        self.client.force_login(_User.objects.get_or_create(username="testuser")[0])
        add_response = self.client.post(
            _reverse("novels:watch-component", kwargs={"novel_id": self.fic.id}), {"watch": True},
        )
        remove_response = self.client.post(
            _reverse("novels:watch-component", kwargs={"novel_id": self.fic.id}), {"watch": False},
        )
        self.assertEqual(add_response.status_code, 302, "The update should return with a redirect")
        self.assertEqual(remove_response.status_code, 302, "The update should return with a redirect")
        updated_response = self.client.get(_reverse("novels:watch-component", kwargs={"novel_id": self.fic.id}))
        self.assertContains(updated_response, "unchecked")  # the watching status should be false again
        self.assertEqual(updated_response.status_code, 200)


class SearchComponentTests(_TestCase):
    def setUp(self):
        parser = _Parser.objects.get(name="rrl novel")
        self.fic = _Fiction.objects.create(title="test fiction", url="https://some.fq.dn/with/uri", source=parser)

    def test_simple_get(self):
        response = self.client.get(_reverse("novels:search"))
        self.assertContains(response, "test fiction")
        self.assertEqual(response.status_code, 200)

    def test_get_context(self):
        self.client.force_login(_User.objects.get_or_create(username="testuser")[0])
        self.test_simple_get()


class NovelListTests(_TestCase):
    def setUp(self):
        parser = _Parser.objects.get(name="rrl novel")
        self.fic = _Fiction.objects.create(title="test fiction", url="https://some.fq.dn/with/uri", source=parser)
        self.chap = _Chapter.objects.create(
            fiction=self.fic, url="https://some.fq.dn/with/chap/uri", content="some content",
        )
        self.watched_fic = _Fiction.objects.create(
            title="another-test-fiction", url="https://some.fq.dn/with/another/uri", source=parser,
        )
        self.user = _User.objects.get_or_create(username="testuser")[0]

    def test_authenticated_get(self):
        self.client.force_login(self.user)
        self.test_simple_get()

    def test_simple_get(self):
        response = self.client.get(_reverse("novels:novels"))
        self.assertEqual(response.status_code, 200)

    def test_populated_toggle(self):
        self.client.force_login(self.user)
        self.fic.watching.add(self.user)
        response = self.client.get(_reverse("novels:novels") + "?populated=true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.fic.title)
        self.assertEqual(
            response.context["novels"].paginator.count, 1, "only one fiction has chapters",
        )

    def test_watching_toggle(self):
        self.client.force_login(self.user)
        self.watched_fic.watching.add(self.user)
        response = self.client.get(_reverse("novels:novels") + "?watching=true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.watched_fic.title)
        self.assertEqual(response.context["novels"].paginator.count, 1, "only one fiction is watched")


class NovelViewTests(_TestCase):
    fixtures = ["2018-10-17.json"]

    def setUp(self):
        self.scraped_fic = _Fiction.objects.exclude(author=None).first()
        self.unscraped_fic = _Fiction.objects.filter(author=None).first()

    def test_authenticated_get(self):
        self.client.force_login(_User.objects.get_or_create(username="testuser")[0])
        self.test_simple_get()

    def test_simple_get(self):
        response = self.client.get(_reverse("novels:novel", kwargs={"novel_id": self.scraped_fic.id}))
        self.assertContains(response, "a novel by")  # check if novel author is shown
        self.assertEqual(response.status_code, 200)

    def test_get_for_unparsed_fiction(self):
        self.client.force_login(_User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(_reverse("novels:novel", kwargs={"novel_id": self.unscraped_fic.id}))
        self.assertEqual(response.status_code, 200)


class ChapterViewTests(_TestCase):
    fixtures = ["2018-10-17.json"]

    def setUp(self):
        self.user, created = _User.objects.get_or_create(username="testuser")
        self.fic = _Fiction.objects.exclude(author=None).first()
        self.chap = _Chapter.objects.exclude(content=None).first()

    def test_unauthenticated_get(self):
        response = self.client.get(_reverse("novels:chapter", kwargs={"chapter_id": self.chap.id}))
        self.assertEqual(
            response.status_code, 302, "unauthenticated users should get a login redirect",
        )

    def test_authenticated_get(self):
        self.client.force_login(self.user)
        response = self.client.get(_reverse("novels:chapter", kwargs={"chapter_id": self.chap.id}))
        self.assertEqual(response.status_code, 200, "there should be a simple http ok")

    def test_finished_reading_progress_get(self):
        self.client.force_login(self.user)
        reading_progress, created = _ReadingProgress.objects.get_or_create(
            user=self.user, chapter=self.chap, defaults={"progress": 100}
        )

        response = self.client.get(_reverse("novels:chapter", kwargs={"chapter_id": self.chap.id}))
        self.assertEqual(response.status_code, 200, "there should be a simple http ok")
        self.assertContains(response, f"window.progress_id = {reading_progress.id};")

    def test_unfinished_reading_progress_get(self):
        self.client.force_login(self.user)
        reading_progress, created = _ReadingProgress.objects.get_or_create(
            user=self.user, chapter=self.chap, defaults={"progress": 20}
        )

        response = self.client.get(_reverse("novels:chapter", kwargs={"chapter_id": self.chap.id}))
        self.assertEqual(response.status_code, 200, "there should be a simple http ok")
        self.assertContains(response, f"{reading_progress.progress}")
        self.assertContains(response, "continue")  # there should be a btn to jump to last progress

    def test_chapter_without_content(self):
        self.client.force_login(self.user)
        self.chap.content = None
        self.chap.save()

        response = self.client.get(_reverse("novels:chapter", kwargs={"chapter_id": self.chap.id}))
        self.assertEqual(response.status_code, 200, "there should be a simple http ok")
        self.assertContains(response, f"always go to the original source")

    def test_chapter_without_content_but_fetch_permission(self):
        permission = _Permission.objects.get(codename="force_fetch")
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)
        self.chap.content = None
        self.chap.save()

        self.assertTrue(
            self.user.has_perm("scrapes.force_fetch"),
            "the user should have the permission to force a fetch for this test",
        )

        response = self.client.get(_reverse("novels:chapter", kwargs={"chapter_id": self.chap.id}))
        self.assertEqual(response.status_code, 200, "there should be a simple http ok")
        self.assertContains(response, f"?force-fetch=true")  # the force fetch link should be in the body
