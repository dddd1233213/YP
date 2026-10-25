from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def home_placeholder(request):
    return HttpResponse("Team Finder")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_placeholder, name="home"),
]
