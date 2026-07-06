from django.urls import path

from apps.moderation import views

app_name = "moderation"

urlpatterns = [
    path("queue/", views.moderation_queue, name="queue"),
    path("review/<int:review_id>/", views.moderation_review, name="review"),
]
