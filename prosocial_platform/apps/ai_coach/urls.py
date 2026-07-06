from django.urls import path

from apps.ai_coach import views

app_name = "ai_coach"

urlpatterns = [
    path("journal/", views.journal_list, name="journal_list"),
    path("journal/new/", views.journal_create, name="journal_create"),
    path("pre-send-check/", views.pre_send_check, name="pre_send_check"),
]
