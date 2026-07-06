from django.urls import path

from apps.advanced import views

app_name = "advanced"

urlpatterns = [
    path("donations/", views.donation_list, name="donation_list"),
    path("donations/new/", views.donation_create_campaign, name="donation_create"),
    path("donations/<uuid:public_id>/", views.donation_detail, name="donation_detail"),
    path("skills/", views.skill_list, name="skill_list"),
    path("skills/new/", views.skill_create, name="skill_create"),
    path("export/", views.data_export, name="data_export"),
]
