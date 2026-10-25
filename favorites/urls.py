from django.urls import path

from favorites.views import FavoriteListView, ToggleFavoriteView

app_name = "favorites"

urlpatterns = [
    path("", FavoriteListView.as_view(), name="list"),
    path(
        "toggle/<int:project_pk>/",
        ToggleFavoriteView.as_view(),
        name="toggle",
    ),
]
