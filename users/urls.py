from django.contrib.auth.views import PasswordChangeDoneView
from django.urls import path

from users.views import (
    CustomLoginView,
    CustomLogoutView,
    CustomPasswordChangeView,
    ProfileDetailView,
    ProfileUpdateView,
    RegisterView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("password-change/", CustomPasswordChangeView.as_view(), name="password_change"),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"),
        name="password_change_done",
    ),
    path("<int:pk>/", ProfileDetailView.as_view(), name="profile"),
    path("<int:pk>/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
]
