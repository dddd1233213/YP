from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from users.models import User


def make_user(email, password="StrongPass123!"):
    return User.objects.create_user(
        email=email,
        password=password,
        first_name="Имя",
        last_name="Фамилия",
    )


class ToggleFavoriteTests(TestCase):
    def setUp(self):
        self.me = make_user("me@example.com")
        self.other = make_user("other@example.com")
        self.project = Project.objects.create(
            title="Проект", author=self.other,
        )
        self.url = reverse(
            "favorites:toggle", args=[self.project.pk],
        )

    def test_guest_redirected_to_login(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_toggle_adds_favorite(self):
        self.client.force_login(self.me)
        detail = reverse("projects:detail", args=[self.project.pk])
        response = self.client.post(self.url, {"next": detail})
        from favorites.models import Favorite
        self.assertTrue(
            Favorite.objects.filter(
                user=self.me, project=self.project).exists()
        )
        self.assertEqual(
            response.url,
            reverse("projects:detail", args=[self.project.pk]),
        )

    def test_toggle_removes_favorite(self):
        from favorites.models import Favorite
        Favorite.objects.create(user=self.me, project=self.project)
        self.client.force_login(self.me)
        detail = reverse("projects:detail", args=[self.project.pk])
        response = self.client.post(self.url, {"next": detail})
        self.assertFalse(
            Favorite.objects.filter(
                user=self.me, project=self.project).exists()
        )
        self.assertEqual(
            response.url,
            reverse("projects:detail", args=[self.project.pk]),
        )

    def test_toggle_evil_next_falls_back_to_detail(self):
        self.client.force_login(self.me)
        response = self.client.post(
            self.url, {"next": "https://evil.test/"})
        self.assertEqual(
            response.url,
            reverse("projects:detail", args=[self.project.pk]),
        )

    def test_toggle_get_not_allowed(self):
        from favorites.models import Favorite
        before = Favorite.objects.count()
        self.client.force_login(self.me)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Favorite.objects.count(), before)

    def test_toggle_get_does_not_remove(self):
        from favorites.models import Favorite
        Favorite.objects.create(user=self.me, project=self.project)
        before = Favorite.objects.count()
        self.client.force_login(self.me)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Favorite.objects.count(), before)

    def test_toggle_without_next_redirects_to_detail(self):
        self.client.force_login(self.me)
        response = self.client.post(self.url)
        self.assertEqual(
            response.url,
            reverse("projects:detail", args=[self.project.pk]),
        )
