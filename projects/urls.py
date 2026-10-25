from django.urls import path

from projects.views import HomeView, ProjectDetailView

app_name = "projects"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="detail"),
]
