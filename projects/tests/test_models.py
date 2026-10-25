from django.db import IntegrityError
from django.test import TestCase

from projects.models import Membership, Project
from users.models import User


def make_user(email, password="StrongPass123!", **kwargs):
    kwargs.setdefault("first_name", "Иван")
    kwargs.setdefault("last_name", "Петров")
    return User.objects.create_user(email=email, password=password, **kwargs)


class ProjectModelTests(TestCase):
    def test_default_status_active(self):
        user = make_user("ivan@example.com")
        project = Project.objects.create(title="Сайт", author=user)
        self.assertEqual(project.status, Project.Status.ACTIVE)

    def test_ordering_newest_first(self):
        user = make_user("ivan@example.com")
        first = Project.objects.create(title="Первый", author=user)
        second = Project.objects.create(title="Второй", author=user)
        self.assertEqual(list(Project.objects.all()), [second, first])

    def test_membership_unique(self):
        owner = make_user("owner@example.com")
        member = make_user("member@example.com")
        project = Project.objects.create(title="Сайт", author=owner)
        Membership.objects.create(user=member, project=project)
        with self.assertRaises(IntegrityError):
            Membership.objects.create(user=member, project=project)
