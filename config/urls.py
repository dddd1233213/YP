from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def home_placeholder(request):
    return HttpResponse("Team Finder")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("", home_placeholder, name="home"),
]
