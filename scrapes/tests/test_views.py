from django.test import TestCase
from django.urls import reverse
from profiles.models import User
from scrapes.managers import Managers
from novels.models import Fiction, Chapter
from django.contrib.auth.models import Permission as _Permission


class ParseLogListViewTests(TestCase):
    fixtures = ["2018-10-17.json"]

    def setUp(self):
        self.managers = Managers()
        self.user = User.objects.get_or_create(username="testuser")[0]
        permission = _Permission.objects.get(codename="view_system")
        self.user.user_permissions.add(permission)

    def test_starting_data(self):
        pending_parses = self.managers.rrl_novel.all_pending_parses()
        self.assertNotEqual(
            pending_parses.count(),
            0,
            "we need something to parse to show up in the log",
        )

    def test_unauthenticated_get(self):
        response = self.client.get(reverse("scrapes:log"))
        self.assertEqual(response.status_code, 302)

    def test_parse_log_context(self):
        self.client.force_login(self.user)
        self.managers.rrl_novel.novel_extractor()
        response = self.client.get(reverse("scrapes:log"))
        self.assertNotEquals(
            response.context["parses"].count(), 0, "Parse Log shouldn't be empty"
        )
        self.assertEqual(response.status_code, 200)


class QueueViewTests(TestCase):
    fixtures = ["2018-10-17.json"]

    def setUp(self):
        self.managers = Managers()
        self.user = User.objects.get_or_create(username="testuser")[0]
        permission = _Permission.objects.get(codename="view_system")
        self.user.user_permissions.add(permission)

    def test_starting_data(self):
        queue = self.managers.manager.scrape_queue()
        self.assertNotEqual(
            queue.count(), 0, "we need something to parse to show up in the log"
        )

    def test_unauthenticated_get(self):
        response = self.client.get(reverse("scrapes:log"))
        self.assertEqual(response.status_code, 302)

    def test_parse_log_context(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("scrapes:queue"))
        self.assertNotEquals(
            response.context["queue"].count(), 0, "Queue shouldn't be empty"
        )
        self.assertEqual(response.status_code, 200)


class HistoryViewTests(TestCase):
    # fixtures = ["2018-10-17.json"]

    def setUp(self):
        self.user = User.objects.get_or_create(username="testuser")[0]
        permission = _Permission.objects.get(codename="view_system")
        self.user.user_permissions.add(permission)
        pass

    def test_unauthenticated_get(self):
        response = self.client.get(reverse("scrapes:history"))
        self.assertEqual(response.status_code, 302)

    def test_parse_log_context(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("scrapes:history"))
        self.assertEqual(response.status_code, 200)
