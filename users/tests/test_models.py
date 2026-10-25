from django.db import IntegrityError
from django.test import TestCase

from users.models import User


class UserModelTests(TestCase):
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            email="ivan@example.com",
            password="secret12345",
            first_name="Иван",
            last_name="Петров",
        )
        self.assertEqual(user.email, "ivan@example.com")
        self.assertTrue(user.check_password("secret12345"))
        self.assertEqual(str(user), "ivan@example.com")

    def test_email_unique(self):
        User.objects.create_user(email="dup@example.com", password="secret12345")
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email="dup@example.com", password="secret12345")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="secret12345"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
