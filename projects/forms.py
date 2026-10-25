from django import forms

from projects.models import Project
from users.forms import BootstrapFormMixin


class ProjectForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ("title", "description")

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("Название проекта обязательно.")
        return title


class ProjectEditForm(ProjectForm):
    class Meta(ProjectForm.Meta):
        fields = ("title", "description", "status")
