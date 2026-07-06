from django.urls import path

from apps.posts import views

app_name = "posts"

urlpatterns = [
    path("create/", views.post_create, name="create"),
    path("<uuid:public_id>/", views.post_detail, name="detail"),
    path("<uuid:public_id>/edit/", views.post_edit, name="edit"),
    path("<uuid:public_id>/delete/", views.post_delete, name="delete"),
]
