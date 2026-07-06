from django.urls import path

from apps.profiles import views

app_name = "profiles"

urlpatterns = [
    path("edit/", views.profile_edit, name="edit"),
    path("<slug:handle>/", views.profile_detail, name="detail"),
]
