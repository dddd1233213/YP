from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
)
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from users.forms import (
    CustomPasswordChangeForm,
    LoginForm,
    ProfileForm,
    RegisterForm,
)
from users.models import User


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        messages.success(self.request, "Регистрация прошла успешно. Теперь войдите.")
        return super().form_valid(form)


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "users/login.html"


class CustomLogoutView(LogoutView):
    pass


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:password_change_done")


class ProfileDetailView(DetailView):
    model = User
    template_name = "users/profile_detail.html"
    context_object_name = "profile_user"


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "users/profile_edit.html"
    context_object_name = "profile_user"
    raise_exception = True

    def test_func(self):
        return self.get_object() == self.request.user

    def get_success_url(self):
        return reverse_lazy("users:profile", args=[self.object.pk])

    def form_valid(self, form):
        messages.success(self.request, "Профиль обновлён.")
        return super().form_valid(form)
