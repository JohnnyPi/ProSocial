from django.urls import path

from apps.gamification import views

app_name = "gamification"

urlpatterns = [
    path("progress/", views.progress_dashboard, name="progress"),
]
