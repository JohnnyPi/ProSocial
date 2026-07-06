from django.urls import path

from apps.engagement import views

app_name = "engagement"

urlpatterns = [
    path("challenges/", views.challenge_list, name="challenges"),
    path(
        "challenges/<int:challenge_id>/complete/",
        views.complete_challenge_view,
        name="complete_challenge",
    ),
    path("rest-mode/", views.rest_mode_toggle, name="rest_mode"),
]
