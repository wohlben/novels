from django.test import TestCase
from django.urls import reverse
from profiles.models import User
from novels.models import Fiction, Chapter


class WatchComponentTests(TestCase):
    def setUp(self):
        self.fic = Fiction.objects.create(
            title="test fiction", url="https://some.fq.dn/with/uri"
        )

    def test_unauthenticated_get(self):
        response = self.client.get(
            reverse("novels:watch-component", kwargs={"novel_id": self.fic.id})
        )
        self.assertEqual(response.status_code, 302)

    def test_get_context(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(
            reverse("novels:watch-component", kwargs={"novel_id": self.fic.id})
        )
        self.assertEquals(
            type(response.context["novel"]),
            Fiction,
            "There should be a Fiction object in the context",
        )
        self.assertContains(
            response, "unchecked"
        )  # the watching status should still be false
        self.assertNotEqual(
            response.context.get("watching"), None, "watching should be defined"
        )
        self.assertEqual(response.status_code, 200)

    def test_add_watching(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.post(
            reverse("novels:watch-component", kwargs={"novel_id": self.fic.id}),
            {"watch": True},
        )
        updated_response = self.client.get(
            reverse("novels:watch-component", kwargs={"novel_id": self.fic.id})
        )
        self.assertContains(
            updated_response, "checked"
        )  # the watching status should be true now
        self.assertEqual(
            response.status_code, 302, "The update should return with a redirect"
        )
        self.assertEqual(updated_response.status_code, 200)

    def test_remove_watching(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        add_response = self.client.post(
            reverse("novels:watch-component", kwargs={"novel_id": self.fic.id}),
            {"watch": True},
        )
        remove_response = self.client.post(
            reverse("novels:watch-component", kwargs={"novel_id": self.fic.id}),
            {"watch": False},
        )
        self.assertEqual(
            add_response.status_code, 302, "The update should return with a redirect"
        )
        self.assertEqual(
            remove_response.status_code, 302, "The update should return with a redirect"
        )
        updated_response = self.client.get(
            reverse("novels:watch-component", kwargs={"novel_id": self.fic.id})
        )
        self.assertContains(
            updated_response, "unchecked"
        )  # the watching status should be false again
        self.assertEqual(updated_response.status_code, 200)


class SearchComponentTests(TestCase):
    def setUp(self):
        self.fic = Fiction.objects.create(
            title="test fiction", url="https://some.fq.dn/with/uri"
        )

    def test_unauthenticated_get(self):
        response = self.client.get(reverse("novels:search"))
        self.assertEqual(response.status_code, 302)

    def test_get_context(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(reverse("novels:search"))
        self.assertContains(
            response, "test fiction"
        )  # the added fiction should be available in the search
        self.assertEqual(response.status_code, 200)


class NovelListTests(TestCase):
    def setUp(self):
        self.fic = Fiction.objects.create(
            title="test fiction", url="https://some.fq.dn/with/uri"
        )
        self.chap = Chapter.objects.create(
            fiction=self.fic,
            url="https://some.fq.dn/with/chap/uri",
            content="some content",
        )
        self.watched_fic = Fiction.objects.create(
            title="another-test-fiction", url="https://some.fq.dn/with/another/uri"
        )
        self.user = User.objects.get_or_create(username="testuser")[0]

    def test_unauthenticated_get(self):
        response = self.client.get(reverse("novels:novels"))
        self.assertContains(response, "login with GitHub")
        self.assertEqual(response.status_code, 200)

    def test_get_context(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("novels:novels"))
        self.assertEqual(response.status_code, 200)

    def test_populated_toggle(self):
        self.client.force_login(self.user)
        self.fic.watching.add(self.user)
        response = self.client.get(reverse("novels:novels") + "?populated=true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.fic.title)
        self.assertEqual(
            response.context["novels"].count(), 1, "only one fiction has chapters"
        )

    def test_watching_toggle(self):
        self.client.force_login(self.user)
        self.watched_fic.watching.add(self.user)
        response = self.client.get(reverse("novels:novels") + "?watching=true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.watched_fic.title)
        self.assertEqual(
            response.context["novels"].count(), 1, "only one fiction is watched"
        )


class NovelViewTests(TestCase):
    fixtures = ["2018-10-17.json"]

    def setUp(self):
        self.scraped_fic = Fiction.objects.exclude(author=None).first()
        self.unscraped_fic = Fiction.objects.filter(author=None).first()

    def test_unauthenticated_get(self):
        response = self.client.get(
            reverse("novels:novel", kwargs={"novel_id": self.scraped_fic.id})
        )
        self.assertContains(response, "login with GitHub")
        self.assertEqual(response.status_code, 200)

    def test_get_context(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(
            reverse("novels:novel", kwargs={"novel_id": self.scraped_fic.id})
        )
        self.assertContains(response, "a novel by")  # check if novel author is shown
        self.assertEqual(response.status_code, 200)

    def test_get_for_unparsed_fiction(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(
            reverse("novels:novel", kwargs={"novel_id": self.unscraped_fic.id})
        )
        self.assertEqual(response.status_code, 200)


class ChapterViewTests(TestCase):
    def setUp(self):
        self.fic = Fiction.objects.create(
            title="test fiction", url="https://some.fq.dn/with/uri"
        )
        self.chap = Chapter.objects.create(
            fiction=self.fic, url="https://some.fq.dn/with/chap/uri"
        )

    def test_unauthenticated_get(self):
        response = self.client.get(
            reverse("novels:chapter", kwargs={"chapter_id": self.chap.id})
        )
        self.assertContains(response, "login with GitHub")
        self.assertEqual(response.status_code, 200)

    def test_get_context(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(
            reverse("novels:chapter", kwargs={"chapter_id": self.chap.id})
        )
        self.assertEqual(response.status_code, 200)
