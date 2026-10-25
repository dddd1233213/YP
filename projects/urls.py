from django.urls import path

from projects.views import ProjectCreateView, ProjectDetailView, ProjectUpdateView

app_name = "projects"

urlpatterns = [
    path("create/", ProjectCreateView.as_view(), name="create"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", ProjectUpdateView.as_view(), name="edit"),
]
