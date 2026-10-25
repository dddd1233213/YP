from django.urls import path

from favorites.views import ToggleFavoriteView

app_name = "favorites"

urlpatterns = [
    path(
        "toggle/<int:project_pk>/",
        ToggleFavoriteView.as_view(),
        name="toggle",
    ),
]
