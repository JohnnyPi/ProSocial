from django.urls import path

from apps.messaging import views

app_name = "messaging"

urlpatterns = [
    path("", views.conversation_list, name="list"),
    path("<uuid:public_id>/", views.conversation_detail, name="detail"),
    path("start/<str:handle>/", views.start_conversation, name="start"),
]
