from django.test import TestCase
from django.urls import reverse
from .models import User


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


class ProfileViewTests(TestCase):
    def test_authenticated_get(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
