from django.urls import path

from apps.profiles import views

app_name = "profiles"

urlpatterns = [
    path("edit/", views.profile_edit, name="edit"),
    path("endorsements/new/", views.endorsement_create, name="endorsement_create"),
    path("<slug:handle>/", views.profile_detail, name="detail"),
]
