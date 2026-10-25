from django.core.management import call_command
from django.test import TestCase

from projects.models import Project
from users.models import User
from users.views import FILTERS

SEED_EMAILS = [
    "anna@example.com",
    "boris@example.com",
    "vera@example.com",
]


class SeedDemoTests(TestCase):
    def test_seed_creates_users_and_projects(self):
        call_command("seed_demo")
        for email in SEED_EMAILS:
            self.assertTrue(
                User.objects.filter(email=email).exists())
        for email in SEED_EMAILS:
            user = User.objects.get(email=email)
            self.assertGreaterEqual(
                Project.objects.filter(author=user).count(), 1)

    def test_seed_is_idempotent(self):
        call_command("seed_demo")
        users_before = User.objects.count()
        projects_before = Project.objects.count()
        call_command("seed_demo")
        self.assertEqual(User.objects.count(), users_before)
        self.assertEqual(Project.objects.count(), projects_before)

    def test_rerun_prints_already_seeded(self):
        call_command("seed_demo")
        from io import StringIO
        out = StringIO()
        call_command("seed_demo", stdout=out)
        self.assertIn("already seeded", out.getvalue())

    def test_seed_relations_cover_all_filters(self):
        call_command("seed_demo")
        anna = User.objects.get(email="anna@example.com")
        boris = User.objects.get(email="boris@example.com")
        vera = User.objects.get(email="vera@example.com")
        self.assertIn(boris, FILTERS["favorite_authors"](anna))
        self.assertIn(boris, FILTERS["my_projects_participants"](anna))
        self.assertIn(vera, FILTERS["my_projects_participants"](anna))
        self.assertIn(vera, FILTERS["fans"](anna))
        self.assertIn(boris, FILTERS["teammates"](anna))
        self.assertIn(anna, FILTERS["fans"](boris))
        self.assertIn(anna, FILTERS["teammates"](boris))

    def test_superuser_alone_does_not_block_seeding(self):
        User.objects.create_superuser(
            email="admin@example.com", password="AdminPass123!",
            first_name="Админ", last_name="Главный")
        call_command("seed_demo")
        for email in SEED_EMAILS:
            self.assertTrue(
                User.objects.filter(email=email).exists())
