import os

from django.core.management.base import BaseCommand
from django.db import transaction

from favorites.models import Favorite
from projects.models import Membership, Project
from users.models import User


class Command(BaseCommand):
    help = "Создать демо-данные: 3 пользователя, проекты, участия, избранное"

    def handle(self, *args, **options):
        if User.objects.exclude(is_superuser=True).exists():
            self.stdout.write("already seeded")
            return
        password = os.environ.get("SEED_PASSWORD", "demo12345")
        source = "env SEED_PASSWORD" if "SEED_PASSWORD" in os.environ else (
            "default demo12345")
        with transaction.atomic():
            anna, _ = User.objects.get_or_create(
                email="anna@example.com",
                defaults={"first_name": "Анна",
                          "last_name": "Соколова",
                          "bio": "Бэкенд-разработчик, люблю Django."},
            )
            anna.set_password(password)
            anna.save()
            boris, _ = User.objects.get_or_create(
                email="boris@example.com",
                defaults={"first_name": "Борис",
                          "last_name": "Волков",
                          "bio": "Фронтенд-разработчик, делаю интерфейсы."},
            )
            boris.set_password(password)
            boris.save()
            vera, _ = User.objects.get_or_create(
                email="vera@example.com",
                defaults={"first_name": "Вера",
                          "last_name": "Орлова",
                          "bio": "Дизайнер и менеджер проектов."},
            )
            vera.set_password(password)
            vera.save()
            anna_p1, _ = Project.objects.get_or_create(
                title="Веб-приложение для команды",
                author=anna,
                defaults={"description": "Поиск людей в команду.",
                          "status": Project.Status.ACTIVE},
            )
            anna_p2, _ = Project.objects.get_or_create(
                title="Архивный проект Анны",
                author=anna,
                defaults={"description": "Завершённый проект.",
                          "status": Project.Status.FINISHED},
            )
            boris_p, _ = Project.objects.get_or_create(
                title="Мобильное приложение",
                author=boris,
                defaults={"description": "Приложение для поиска команд.",
                          "status": Project.Status.ACTIVE},
            )
            vera_p, _ = Project.objects.get_or_create(
                title="Дизайн-система",
                author=vera,
                defaults={"description": "Компоненты интерфейса.",
                          "status": Project.Status.ACTIVE},
            )
            Membership.objects.get_or_create(user=boris, project=anna_p1)
            Membership.objects.get_or_create(user=anna, project=boris_p)
            Membership.objects.get_or_create(user=vera, project=anna_p1)
            Favorite.objects.get_or_create(user=anna, project=boris_p)
            Favorite.objects.get_or_create(user=vera, project=anna_p1)
        for email in ("anna@example.com",
                      "boris@example.com", "vera@example.com"):
            self.stdout.write(f"created {email}")
        self.stdout.write(f"password source: {source}")
