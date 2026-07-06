from django.urls import path

from apps.prosocial_actions import views

app_name = "prosocial_actions"

urlpatterns = [
    path("actions/", views.action_list, name="action_list"),
    path("actions/create/", views.action_create, name="action_create"),
    path("actions/verification-queue/", views.verification_queue, name="verification_queue"),
    path("actions/<uuid:public_id>/", views.action_detail, name="action_detail"),
    path("actions/<uuid:public_id>/cancel/", views.action_cancel, name="action_cancel"),
    path("actions/<uuid:public_id>/save/", views.action_save, name="action_save"),
    path("actions/<uuid:public_id>/commit/", views.action_commit, name="action_commit"),
    path("actions/<uuid:public_id>/withdraw/", views.action_withdraw, name="action_withdraw"),
    path("actions/<uuid:public_id>/complete/", views.action_complete, name="action_complete"),
    path("actions/<uuid:public_id>/invite/", views.action_invite, name="action_invite"),
    path("commitments/", views.commitment_list, name="commitment_list"),
    path("commitments/<uuid:public_id>/", views.commitment_detail, name="commitment_detail"),
    path("commitments/<uuid:public_id>/verify/", views.commitment_verify, name="commitment_verify"),
    path("commitments/<uuid:public_id>/reject/", views.commitment_reject, name="commitment_reject"),
    path(
        "commitments/<uuid:public_id>/acknowledge/",
        views.commitment_acknowledge,
        name="commitment_acknowledge",
    ),
    path("invitations/", views.invitation_list, name="invitations"),
    path("invitations/<uuid:public_id>/accept/", views.invitation_accept, name="invitation_accept"),
    path(
        "invitations/<uuid:public_id>/decline/", views.invitation_decline, name="invitation_decline"
    ),
]
