from django.conf import settings
from django.db import models


class Project(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активен"
        FINISHED = "finished", "Завершён"

    title = models.CharField("название", max_length=200)
    description = models.TextField("описание", blank=True)
    status = models.CharField(
        "статус", max_length=8, choices=Status.choices, default=Status.ACTIVE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="автор",
    )
    created_at = models.DateTimeField("создан", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "проект"
        verbose_name_plural = "проекты"

    def __str__(self):
        return self.title


class Membership(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="участник",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="проект",
    )
    joined_at = models.DateTimeField("вступил", auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")
        verbose_name = "участие"
        verbose_name_plural = "участия"

    def __str__(self):
        return f"{self.user} в {self.project}"
