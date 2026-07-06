from django.urls import path

from apps.trust import views

app_name = "trust"

urlpatterns = [
    path("onboarding/", views.onboarding, name="onboarding"),
    path("settings/", views.trust_settings, name="settings"),
]
