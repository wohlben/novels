from django.test import TestCase
from django.urls import reverse
from .models import User


class LoginViewTests(TestCase):
    def test_unauthenticated_get(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Login with GitHub")
        self.assertEqual(response.status_code, 200)

class ProfileViewTests(TestCase):
    def test_authenticated_get(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
