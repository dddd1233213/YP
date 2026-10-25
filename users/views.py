from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
)
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from users.forms import (
    CustomPasswordChangeForm,
    LoginForm,
    ProfileForm,
    RegisterForm,
)
from users.models import User


FILTERS = {
    "my_projects_participants": lambda user: User.objects.filter(
        membership__project__author=user
    ).distinct(),
    "teammates": lambda user: User.objects.filter(
        projects__memberships__user=user
    ).distinct(),
    "favorite_authors": lambda user: User.objects.filter(
        projects__favorited_by__user=user
    ).exclude(pk=user.pk).distinct(),
    "fans": lambda user: User.objects.filter(
        favorites__project__author=user
    ).exclude(pk=user.pk).distinct(),
}


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


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    paginate_by = 12
    ordering = "-date_joined"

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_name = self.request.GET.get("filter")
        if not self.request.user.is_authenticated:
            return queryset
        if filter_name not in FILTERS:
            return queryset
        return FILTERS[filter_name](self.request.user).order_by("-date_joined")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_name = self.request.GET.get("filter")
        if self.request.user.is_authenticated and filter_name in FILTERS:
            context["active_filter"] = filter_name
        else:
            context["active_filter"] = ""
        return context
