from django.test import TestCase
from django.urls import reverse

from projects.models import Membership, Project
from users.models import User


def make_user(email, password="StrongPass123!", **kwargs):
    kwargs.setdefault("first_name", "Имя")
    kwargs.setdefault("last_name", "Фамилия")
    return User.objects.create_user(email=email, password=password, **kwargs)


class UserListFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = [
            make_user(f"user{i}@example.com", first_name=f"Имя{i}")
            for i in range(5)
        ]
        cls.me = cls.users[0]
        authors = [cls.users[0], cls.users[0], cls.users[1],
                   cls.users[2], cls.users[3]]
        cls.projects = [
            Project.objects.create(
                title=f"Проект {i}", author=author,
            )
            for i, author in enumerate(authors)
        ]
        Membership.objects.create(user=cls.users[1], project=cls.projects[0])
        Membership.objects.create(user=cls.users[2], project=cls.projects[0])
        Membership.objects.create(user=cls.users[3], project=cls.projects[1])
        Membership.objects.create(user=cls.me, project=cls.projects[2])
        Membership.objects.create(user=cls.me, project=cls.projects[3])

    def setUp(self):
        self.client.force_login(self.me)
        self.url = reverse("users:list")

    def test_my_projects_participants(self):
        response = self.client.get(
            self.url, {"filter": "my_projects_participants"})
        self.assertEqual(response.status_code, 200)
        got = set(response.context["users"])
        self.assertEqual(got, {self.users[1], self.users[2], self.users[3]})
        ordered = list(response.context["users"])
        expected = sorted(
            [self.users[1], self.users[2], self.users[3]],
            key=lambda u: u.date_joined, reverse=True,
        )
        self.assertEqual([u.pk for u in ordered], [u.pk for u in expected])

    def test_teammates(self):
        response = self.client.get(self.url, {"filter": "teammates"})
        self.assertEqual(response.status_code, 200)
        got = list(response.context["users"])
        self.assertEqual(
            [u.pk for u in got],
            [u.pk for u in sorted(
                [self.users[1], self.users[2]],
                key=lambda u: u.date_joined, reverse=True,
            )],
        )

    def test_bogus_filter_returns_full_list(self):
        response = self.client.get(self.url, {"filter": "bogus"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(list(response.context["users"])), 5)

    def test_panel_visible_for_authenticated(self):
        response = self.client.get(
            self.url, {"filter": "my_projects_participants"})
        self.assertContains(response, "?filter=my_projects_participants")
        self.assertContains(response, "?filter=teammates")
        self.assertContains(response, 'class="active"')

    def test_panel_hidden_for_guest(self):
        self.client.logout()
        response = self.client.get(
            self.url, {"filter": "my_projects_participants"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "?filter=my_projects_participants")
        self.assertNotContains(response, "?filter=teammates")

    def test_reset_link(self):
        response = self.client.get(
            self.url, {"filter": "my_projects_participants"})
        self.assertContains(response, f'href="{self.url}"')

    def test_pagination_preserves_filter(self):
        for i in range(13):
            extra = make_user(f"extra{i}@example.com")
            Membership.objects.create(user=extra, project=self.projects[0])
        response = self.client.get(
            self.url, {"filter": "my_projects_participants"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertContains(
            response, "filter=my_projects_participants&page=2")

    def test_queries_my_projects_participants(self):
        with self.assertNumQueries(4):
            self.client.get(self.url, {"filter": "my_projects_participants"})

    def test_queries_teammates(self):
        with self.assertNumQueries(4):
            self.client.get(self.url, {"filter": "teammates"})

    def test_queries_bogus(self):
        with self.assertNumQueries(4):
            self.client.get(self.url, {"filter": "bogus"})
