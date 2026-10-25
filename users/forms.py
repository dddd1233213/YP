from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

from users.models import User


class BootstrapFormMixin:
    """Add Bootstrap classes to every widget.

    Reusable across the project: mix into any future form
    (ProjectForm, ProfileForm) instead of styling fields by hand.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = "form-check-input"
            else:
                css_class = "form-control"
            existing = field.widget.attrs.get("class", "")
            if css_class not in existing.split():
                field.widget.attrs["class"] = f"{existing} {css_class}".strip()


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class CustomPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    pass


def validate_avatar(value):
    if value.content_type not in ("image/jpeg", "image/png",
                                  "image/gif", "image/webp"):
        raise forms.ValidationError("Загрузите файл изображения (JPEG/PNG/GIF/WebP).")
    if value.size > 2 * 1024 * 1024:
        raise forms.ValidationError("Размер аватара не должен превышать 2 МБ.")


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    avatar = forms.ImageField(required=False, validators=[validate_avatar])

    class Meta:
        model = User
        fields = ("first_name", "last_name", "bio", "phone", "github", "avatar")
