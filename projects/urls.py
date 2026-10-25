from django.urls import path

from projects.views import (
    FinishView,
    JoinView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectUpdateView,
)

app_name = "projects"

urlpatterns = [
    path("create/", ProjectCreateView.as_view(), name="create"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", ProjectUpdateView.as_view(), name="edit"),
    path("<int:pk>/join/", JoinView.as_view(), name="join"),
    path("<int:pk>/finish/", FinishView.as_view(), name="finish"),
]
