from django.urls import path

from apps.discovery import views

app_name = "discovery"

urlpatterns = [
    path("", views.discovery_home, name="home"),
    path("ripple/", views.ripple_effect, name="ripple"),
]
