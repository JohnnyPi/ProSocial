from django.urls import path

from apps.moderation import views

app_name = "moderation"

urlpatterns = [
    path("queue/", views.moderation_queue, name="queue"),
    path("review/<int:review_id>/", views.moderation_review, name="review"),
    path("appeal/<int:action_id>/", views.appeal_create, name="appeal_create"),
    path("appeals/<int:appeal_id>/review/", views.appeal_review, name="appeal_review"),
    path("history/", views.moderation_history, name="history"),
]
