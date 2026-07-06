from django.urls import path

from apps.guilds import views

app_name = "guilds"

urlpatterns = [
    path("", views.guild_list, name="list"),
    path("new/", views.guild_create, name="create"),
    path("<slug:slug>/", views.guild_detail, name="detail"),
    path("<slug:slug>/join/", views.guild_join, name="join"),
    path("<slug:slug>/leave/", views.guild_leave, name="leave"),
]
