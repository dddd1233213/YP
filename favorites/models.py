from django.conf import settings
from django.db import models

from projects.models import Project


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="пользователь",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="проект",
    )
    created_at = models.DateTimeField("добавлен", auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")
        verbose_name = "избранное"
        verbose_name_plural = "избранное"

    def __str__(self):
        return f"{self.user} → {self.project}"
