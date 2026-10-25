from django.views.generic import DetailView, ListView

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
