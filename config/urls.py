from django.contrib import admin
from django.urls import include, path

from projects.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("projects/", include("projects.urls")),
]
