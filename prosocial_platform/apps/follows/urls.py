from django.urls import path

from apps.follows import views

app_name = "follows"

urlpatterns = [
    path("follow/user/<str:handle>/", views.toggle_follow_user, name="toggle_user"),
    path("follow/post/<uuid:post_id>/", views.toggle_follow_post, name="toggle_post"),
]
