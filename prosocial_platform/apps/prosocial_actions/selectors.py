import uuid

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.prosocial_actions.models import (
    ActionInvitation,
    ActionOpportunity,
    ActionStatus,
    Commitment,
    CommitmentStatus,
    InvitationStatus,
)


def get_open_actions(*, kind: str | None = None) -> QuerySet[ActionOpportunity]:
    qs = (
        ActionOpportunity.objects.filter(status=ActionStatus.OPEN)
        .select_related("post", "post__author__profile", "creator")
        .order_by("-created_at")
    )
    if kind:
        qs = qs.filter(post__kind=kind)
    return qs


def get_action_detail(*, public_id: uuid.UUID) -> ActionOpportunity:
    return get_object_or_404(
        ActionOpportunity.objects.select_related("post", "post__author__profile", "creator"),
        public_id=public_id,
    )


def get_user_commitments(*, user, include_saved: bool = True) -> QuerySet[Commitment]:
    statuses = [
        CommitmentStatus.COMMITTED,
        CommitmentStatus.COMPLETION_SUBMITTED,
        CommitmentStatus.VERIFIED,
    ]
    if include_saved:
        statuses.insert(0, CommitmentStatus.SAVED)
    return (
        Commitment.objects.filter(participant=user, status__in=statuses)
        .select_related("action", "action__post")
        .order_by("-updated_at")
    )


def get_pending_verifications(*, creator) -> QuerySet[Commitment]:
    return Commitment.objects.filter(
        action__creator=creator,
        status=CommitmentStatus.COMPLETION_SUBMITTED,
        completion_submission__review_status="PENDING",
    ).select_related("participant", "action", "completion_submission")


def get_pending_invitations(*, user) -> QuerySet[ActionInvitation]:
    return ActionInvitation.objects.filter(
        invitee=user, status=InvitationStatus.PENDING
    ).select_related("action", "inviter", "action__post")


def get_due_reminders(*, now=None):
    now = now or timezone.now()
    return Commitment.objects.filter(
        reminders_enabled=True,
        reminder_at__lte=now,
        reminder_dispatched_at__isnull=True,
        status__in=[CommitmentStatus.COMMITTED, CommitmentStatus.SAVED],
    ).select_related("participant", "action")
