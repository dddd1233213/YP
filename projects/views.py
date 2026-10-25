from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from projects.forms import ProjectEditForm, ProjectForm
from projects.models import Membership, Project


class HomeView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fav_ids"] = set()
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        user = self.request.user
        context["is_member"] = (
            user.is_authenticated
            and Membership.objects.filter(user=user, project=project).exists()
        )
        context["is_fav"] = False  # Task 6 wires real state
        context["fav_ids"] = set()
        context["participants"] = project.memberships.select_related("user").all()
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Проект создан.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("projects:detail", args=[self.object.pk])


class OwnerRequiredMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.get_object().author == self.request.user


class ProjectUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectEditForm
    template_name = "projects/project_form.html"
    context_object_name = "project"

    def form_valid(self, form):
        messages.success(self.request, "Проект обновлён.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("projects:detail", args=[self.object.pk])


class JoinView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.author == request.user:
            messages.info(request, "Вы автор этого проекта.")
            return redirect("projects:detail", pk=project.pk)
        membership, created = Membership.objects.get_or_create(
            user=request.user, project=project
        )
        if created:
            messages.success(request, "Вы присоединились к проекту.")
        else:
            messages.info(request, "Вы уже участник этого проекта.")
        return redirect("projects:detail", pk=project.pk)


class FinishView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.author != request.user:
            raise PermissionDenied
        if project.status == Project.Status.ACTIVE:
            project.status = Project.Status.FINISHED
            project.save(update_fields=["status"])
            messages.success(request, "Проект завершён.")
        else:
            messages.info(request, "Проект уже завершён.")
        return redirect("projects:detail", pk=project.pk)
