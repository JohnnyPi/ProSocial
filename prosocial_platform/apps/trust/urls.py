from django.urls import path

from apps.trust import views

app_name = "trust"

urlpatterns = [
    path("onboarding/", views.onboarding, name="onboarding"),
    path("settings/", views.trust_settings, name="settings"),
    path("rate/reply/<uuid:reply_id>/", views.rate_reply, name="rate_reply"),
    path("rate/post/<uuid:post_id>/", views.rate_post, name="rate_post"),
]
