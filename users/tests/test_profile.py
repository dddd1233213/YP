from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from users.models import User


def make_user(email, password="StrongPass123!", **kwargs):
    kwargs.setdefault("first_name", "Иван")
    kwargs.setdefault("last_name", "Петров")
    return User.objects.create_user(email=email, password=password, **kwargs)


class ProfileViewTests(TestCase):
    def test_profile_guest_200(self):
        user = make_user("ivan@example.com")
        response = self.client.get(reverse("users:profile", args=[user.pk]))
        self.assertEqual(response.status_code, 200)

    def test_owner_buttons_only_for_owner(self):
        owner = make_user("owner@example.com")
        make_user("other@example.com")
        url = reverse("users:profile", args=[owner.pk])
        self.client.login(username="other@example.com", password="StrongPass123!")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Редактировать профиль")
        self.client.logout()
        self.client.login(username="owner@example.com", password="StrongPass123!")
        response = self.client.get(url)
        self.assertContains(response, "Редактировать профиль")

    def test_edit_by_other_forbidden(self):
        owner = make_user("owner@example.com")
        make_user("other@example.com")
        self.client.login(username="other@example.com", password="StrongPass123!")
        url = reverse("users:profile_edit", args=[owner.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_edit_own_post_updates(self):
        make_user("ivan@example.com", first_name="Иван")
        self.client.login(username="ivan@example.com", password="StrongPass123!")
        user = User.objects.get(email="ivan@example.com")
        url = reverse("users:profile_edit", args=[user.pk])
        response = self.client.post(url, {
            "first_name": "Пётр",
            "last_name": "Петров",
            "bio": "Backend-разработчик",
            "phone": "+7 999 123-45-67",
            "github": "https://github.com/ivan",
        })
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Пётр")
        self.assertEqual(user.bio, "Backend-разработчик")

    def test_contacts_button_in_html(self):
        user = make_user("ivan@example.com")
        response = self.client.get(reverse("users:profile", args=[user.pk]))
        self.assertContains(response, "Посмотреть контакты")


class ProfileFormAvatarTests(TestCase):
    def test_avatar_oversize_non_image_invalid(self):
        from users.forms import ProfileForm

        big = SimpleUploadedFile(
            "evil.bin", b"x" * (10 * 1024 * 1024), content_type="text/plain"
        )
        form = ProfileForm(
            data={"first_name": "И", "last_name": "П"},
            files={"avatar": big},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("avatar", form.errors)

    def test_avatar_valid_image_oversize_invalid(self):
        import io
        import os

        from PIL import Image

        from users.forms import ProfileForm

        raw = os.urandom(1200 * 1200 * 3)
        img = Image.frombytes("RGB", (1200, 1200), raw)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        self.assertGreater(buf.tell(), 2 * 1024 * 1024)
        big_png = SimpleUploadedFile(
            "big.png", buf.getvalue(), content_type="image/png"
        )
        form = ProfileForm(
            data={"first_name": "И", "last_name": "П"},
            files={"avatar": big_png},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("avatar", form.errors)
        self.assertTrue(
            any("2 МБ" in e for e in form.errors["avatar"])
        )
