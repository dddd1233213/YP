from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from favorites.models import Favorite
from projects.models import Project


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        fav, created = Favorite.objects.get_or_create(
            user=request.user, project=project,
        )
        if created:
            messages.success(request, "Добавлено в избранное.")
        else:
            fav.delete()
            messages.success(request, "Убрано из избранного.")
        next_url = request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()},
        ):
            return redirect(next_url)
        return redirect("projects:detail", pk=project.pk)
