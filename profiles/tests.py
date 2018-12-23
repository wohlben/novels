from django.test import TestCase
from django.urls import reverse


class LoginViewTests(TestCase):
    def test_unauthenticated_get(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Login with GitHub")
        self.assertEqual(response.status_code, 200)
