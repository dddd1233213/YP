from django.test import TestCase
from django.urls import reverse

from users.models import User

REGISTER_URL = reverse("users:register")
LOGIN_URL = reverse("users:login")
LOGOUT_URL = reverse("users:logout")
PASSWORD_CHANGE_URL = reverse("users:password_change")


class AuthViewTests(TestCase):
    def test_register_get_200(self):
        response = self.client.get(REGISTER_URL)
        self.assertEqual(response.status_code, 200)

    def test_login_get_200(self):
        response = self.client.get(LOGIN_URL)
        self.assertEqual(response.status_code, 200)

    def test_register_post_valid_redirects_to_login(self):
        response = self.client.post(REGISTER_URL, {
            "first_name": "Иван",
            "last_name": "Петров",
            "email": "ivan@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertRedirects(response, LOGIN_URL)
        self.assertTrue(User.objects.filter(email="ivan@example.com").exists())

    def test_login_post_valid_redirects_to_home(self):
        User.objects.create_user(
            email="ivan@example.com",
            password="StrongPass123!",
            first_name="Иван",
            last_name="Петров",
        )
        response = self.client.post(LOGIN_URL, {
            "username": "ivan@example.com",
            "password": "StrongPass123!",
        })
        self.assertRedirects(response, "/")

    def test_logout_post_redirects(self):
        User.objects.create_user(
            email="ivan@example.com",
            password="StrongPass123!",
            first_name="Иван",
            last_name="Петров",
        )
        self.client.login(username="ivan@example.com", password="StrongPass123!")
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 302)

    def test_password_change_requires_login(self):
        response = self.client.get(PASSWORD_CHANGE_URL)
        self.assertEqual(response.status_code, 302)
