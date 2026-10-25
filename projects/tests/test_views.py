from django.test import TestCase
from django.urls import reverse

from projects.models import Membership, Project
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

    def test_create_button_only_for_authenticated(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertNotContains(response, "Создать проект")
        make_user("ivan@example.com")
        self.client.login(username="ivan@example.com", password="StrongPass123!")
        response = self.client.get(url)
        self.assertContains(response, "Создать проект")


class ProjectCreateViewTests(TestCase):
    def test_guest_redirected_to_login(self):
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response["Location"])

    def test_post_creates_and_redirects_to_detail(self):
        make_user("ivan@example.com")
        self.client.login(username="ivan@example.com", password="StrongPass123!")
        response = self.client.post(reverse("projects:create"), {
            "title": "Новый проект",
            "description": "Описание",
        })
        project = Project.objects.get(title="Новый проект")
        self.assertRedirects(response, reverse("projects:detail", args=[project.pk]))

    def test_create_form_has_no_status_field(self):
        make_user("ivan@example.com")
        self.client.login(username="ivan@example.com", password="StrongPass123!")
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="status"')


class ProjectUpdateViewTests(TestCase):
    def test_edit_by_other_forbidden(self):
        make_user("owner@example.com")
        make_user("other@example.com")
        project = make_project(User.objects.get(email="owner@example.com"))
        self.client.login(username="other@example.com", password="StrongPass123!")
        url = reverse("projects:edit", args=[project.pk])
        self.assertEqual(self.client.get(url).status_code, 403)
        response = self.client.post(url, {
            "title": "Взлом",
            "description": "",
            "status": "finished",
        })
        self.assertEqual(response.status_code, 403)
        project.refresh_from_db()
        self.assertNotEqual(project.title, "Взлом")

    def test_owner_post_updates_and_redirects(self):
        make_user("owner@example.com")
        self.client.login(username="owner@example.com", password="StrongPass123!")
        project = make_project(User.objects.get(email="owner@example.com"))
        url = reverse("projects:edit", args=[project.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="status"')
        response = self.client.post(url, {
            "title": "Обновлённый",
            "description": "Новое описание",
            "status": "finished",
        })
        self.assertRedirects(response, reverse("projects:detail", args=[project.pk]))
        project.refresh_from_db()
        self.assertEqual(project.title, "Обновлённый")
        self.assertEqual(project.status, Project.Status.FINISHED)


class JoinViewTests(TestCase):
    def test_guest_redirected_to_login(self):
        owner = make_user("owner@example.com")
        project = make_project(owner)
        response = self.client.post(reverse("projects:join", args=[project.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response["Location"])

    def test_owner_post_no_membership(self):
        make_user("owner@example.com")
        self.client.login(username="owner@example.com", password="StrongPass123!")
        project = make_project(User.objects.get(email="owner@example.com"))
        response = self.client.post(reverse("projects:join", args=[project.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Membership.objects.count(), 0)
        response = self.client.get(reverse("projects:detail", args=[project.pk]))
        self.assertNotContains(response, "Присоединиться")

    def test_other_post_creates_membership(self):
        make_project(make_user("owner@example.com"))
        make_user("member@example.com")
        self.client.login(username="member@example.com", password="StrongPass123!")
        project = Project.objects.get()
        response = self.client.post(reverse("projects:join", args=[project.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Membership.objects.filter(
            user__email="member@example.com", project=project).exists())

    def test_double_post_no_duplicate_no_500(self):
        make_project(make_user("owner@example.com"))
        make_user("member@example.com")
        self.client.login(username="member@example.com", password="StrongPass123!")
        project = Project.objects.get()
        url = reverse("projects:join", args=[project.pk])
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Membership.objects.filter(project=project).count(), 1)


class FinishViewTests(TestCase):
    def test_finish_by_other_forbidden(self):
        owner = make_user("owner@example.com")
        make_user("other@example.com")
        project = make_project(owner)
        self.client.login(username="other@example.com", password="StrongPass123!")
        response = self.client.post(reverse("projects:finish", args=[project.pk]))
        self.assertEqual(response.status_code, 403)
        project.refresh_from_db()
        self.assertEqual(project.status, Project.Status.ACTIVE)

    def test_owner_post_finishes(self):
        make_user("owner@example.com")
        self.client.login(username="owner@example.com", password="StrongPass123!")
        project = make_project(User.objects.get(email="owner@example.com"))
        response = self.client.post(reverse("projects:finish", args=[project.pk]))
        self.assertEqual(response.status_code, 302)
        project.refresh_from_db()
        self.assertEqual(project.status, Project.Status.FINISHED)

    def test_double_finish_no_error(self):
        make_user("owner@example.com")
        self.client.login(username="owner@example.com", password="StrongPass123!")
        project = make_project(User.objects.get(email="owner@example.com"))
        url = reverse("projects:finish", args=[project.pk])
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        project.refresh_from_db()
        self.assertEqual(project.status, Project.Status.FINISHED)


class ProjectDetailViewTests(TestCase):
    def test_share_link_in_html(self):
        owner = make_user("owner@example.com")
        project = make_project(owner)
        response = self.client.get(reverse("projects:detail", args=[project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Поделиться")
