from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from users.models import User


def make_user(email, password="StrongPass123!", **kwargs):
    kwargs.setdefault("first_name", "Иван")
    kwargs.setdefault("last_name", "Петров")
    return User.objects.create_user(email=email, password=password, **kwargs)


def make_project(author, title="Проект"):
    return Project.objects.create(title=title, author=author)


class HomeViewTests(TestCase):
    def test_home_200_ordering_and_pagination(self):
        owner = make_user("owner@example.com")
        for i in range(13):
            make_project(owner, title=f"Проект {i:02d}")
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        projects = list(response.context["projects"])
        self.assertEqual(len(projects), 12)
        created = [p.created_at for p in projects]
        self.assertEqual(created, sorted(created, reverse=True))
        response2 = self.client.get(url + "?page=2")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(list(response2.context["projects"])), 1)


class ProjectDetailViewTests(TestCase):
    def test_share_link_in_html(self):
        owner = make_user("owner@example.com")
        project = make_project(owner)
        response = self.client.get(reverse("projects:detail", args=[project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Поделиться")
