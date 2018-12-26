from django.test import TestCase
from django.urls import reverse
from .models import User
from uuid import uuid4


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.get_or_create(
            username="testuser", defaults={"enable_login_token": True}
        )[0]
        self.client.force_login(self.user)

    def test_logout_view(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(
            response.status_code, 200, "response should be a simple http ok"
        )
        self.assertContains(response, "logged out")
        self.assertFalse(response.context['user'].is_authenticated)

class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.get_or_create(
            username="testuser", defaults={"enable_login_token": True}
        )[0]

    def test_unauthenticated_get(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Login with GitHub")
        self.assertEqual(
            response.status_code, 200, "response should be a simple http ok"
        )

    def test_login_token_login(self):
        response = self.client.get(
            f"{reverse('login')}?login_token={self.user.login_token}"
        )
        self.assertEqual(
            response.status_code, 302, "response should be a redirect to home"
        )
        self.assertRedirects(
            response,
            reverse("home"),
            target_status_code=302,
            msg_prefix="sucessfull login should redirect to home",
        )

    def test_disabled_login_token_login(self):
        self.user.enable_login_token = False
        self.user.save()
        response = self.client.get(
            f"{reverse('login')}?login_token={self.user.login_token}"
        )
        self.assertContains(response, "Login with GitHub")
        self.assertEqual(
            response.status_code, 200, "response should be a simple http ok"
        )

    def test_invalid_login_token_login(self):
        response = self.client.get(
            f"{reverse('login')}?login_token={uuid4()}"
        )
        self.assertContains(response, "Login with GitHub")
        self.assertEqual(
            response.status_code, 200, "response should be a simple http ok"
        )

class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.get_or_create(
            username="testuser", defaults={"enable_login_token": False}
        )[0]
        self.client.force_login(self.user)

    def test_authenticated_get(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

    def test_login_token_visible(self):
        self.user.enable_login_token = True
        self.user.save()
        response = self.client.get(reverse("profile"))
        self.assertContains(response, self.user.login_token)
