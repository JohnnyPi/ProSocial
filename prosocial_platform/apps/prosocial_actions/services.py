
from django.db import transaction
from django.utils import timezone

from apps.interactions.models import Notification, NotificationKind
from apps.interactions.selectors import is_blocked
from apps.posts.models import PostKind
from apps.posts.services import create_post
from apps.prosocial_actions.exceptions import ProsocialActionError, validate_transition
from apps.prosocial_actions.models import (
    ActionAcknowledgement,
    ActionInvitation,
    ActionOpportunity,
    ActionStatus,
    Commitment,
    CommitmentStatus,
    CompletionSubmission,
    InvitationStatus,
    ReviewStatus,
    VerificationMode,
)

ACTION_KINDS = {
    PostKind.HELP_REQUEST,
    PostKind.HELP_OFFER,
    PostKind.ENCOURAGEMENT_REQUEST,
    PostKind.LOCAL_ACTION,
    PostKind.VOLUNTEER_OPPORTUNITY,
}


@transaction.atomic
def create_action_post(
    *,
    creator,
    kind: str,
    body: str,
    location_label: str = "",
    starts_at=None,
    ends_at=None,
    capacity: int | None = None,
    verification_mode: str = VerificationMode.SELF_REPORTED,
    completion_instructions: str = "",
    image=None,
    image_alt_text: str = "",
) -> ActionOpportunity:
    if kind not in ACTION_KINDS:
        raise ProsocialActionError("This post kind requires an action opportunity.")
    post = create_post(
        author=creator,
        body=body,
        image=image,
        image_alt_text=image_alt_text,
    )
    post.kind = kind
    post.save(update_fields=["kind", "updated_at"])
    action = ActionOpportunity(
        post=post,
        creator=creator,
        location_label=location_label.strip(),
        starts_at=starts_at,
        ends_at=ends_at,
        capacity=capacity,
        verification_mode=verification_mode,
        completion_instructions=completion_instructions.strip(),
    )
    action.full_clean()
    action.save()
    return action


@transaction.atomic
def update_action(*, action: ActionOpportunity, **fields) -> ActionOpportunity:
    if action.creator_id != fields.pop("_actor", action.creator).pk:
        raise ProsocialActionError("Only the creator can edit this action.")
    for key, value in fields.items():
        if hasattr(action, key):
            setattr(action, key, value)
    action.full_clean()
    action.save()
    return action


@transaction.atomic
def cancel_action(*, action: ActionOpportunity, actor) -> ActionOpportunity:
    if action.creator_id != actor.pk:
        raise ProsocialActionError("Only the creator can cancel this action.")
    action.status = ActionStatus.CANCELLED
    action.save(update_fields=["status", "updated_at"])
    return action


@transaction.atomic
def save_action(*, action: ActionOpportunity, participant) -> Commitment:
    if not action.accepts_commitments:
        raise ProsocialActionError("This action is no longer accepting commitments.")
    commitment, created = Commitment.objects.get_or_create(
        action=action,
        participant=participant,
        defaults={"status": CommitmentStatus.SAVED},
    )
    if not created and commitment.status not in (CommitmentStatus.SAVED, CommitmentStatus.WITHDRAWN):
        raise ProsocialActionError("You already have an active commitment to this action.")
    if commitment.status == CommitmentStatus.WITHDRAWN:
        commitment.status = CommitmentStatus.SAVED
        commitment.withdrawn_at = None
        commitment.save(update_fields=["status", "withdrawn_at", "updated_at"])
    return commitment


@transaction.atomic
def commit_to_action(
    *,
    action: ActionOpportunity,
    participant,
    scheduled_for=None,
    reminder_at=None,
    private_note: str = "",
    is_public: bool = False,
) -> Commitment:
    if not action.accepts_commitments:
        raise ProsocialActionError("This action is no longer accepting commitments.")
    if reminder_at and scheduled_for and reminder_at > scheduled_for:
        raise ProsocialActionError("Reminder cannot occur after scheduled participation.")
    commitment = save_action(action=action, participant=participant)
    validate_transition(commitment.status, CommitmentStatus.COMMITTED)
    commitment.status = CommitmentStatus.COMMITTED
    commitment.scheduled_for = scheduled_for
    commitment.reminder_at = reminder_at
    commitment.private_note = private_note.strip()
    commitment.is_public = is_public
    commitment.committed_at = timezone.now()
    commitment.save()
    return commitment


@transaction.atomic
def withdraw_commitment(*, commitment: Commitment, participant) -> Commitment:
    if commitment.participant_id != participant.pk:
        raise ProsocialActionError("Not authorized.")
    if commitment.status in (CommitmentStatus.VERIFIED, CommitmentStatus.WITHDRAWN):
        raise ProsocialActionError("This commitment cannot be withdrawn.")
    validate_transition(commitment.status, CommitmentStatus.WITHDRAWN)
    commitment.status = CommitmentStatus.WITHDRAWN
    commitment.withdrawn_at = timezone.now()
    commitment.save(update_fields=["status", "withdrawn_at", "updated_at"])
    return commitment


@transaction.atomic
def submit_completion(*, commitment: Commitment, participant, note: str = "") -> CompletionSubmission:
    if commitment.participant_id != participant.pk:
        raise ProsocialActionError("Not authorized.")
    validate_transition(commitment.status, CommitmentStatus.COMPLETION_SUBMITTED)
    if hasattr(commitment, "completion_submission"):
        raise ProsocialActionError("Completion already submitted.")
    commitment.status = CommitmentStatus.COMPLETION_SUBMITTED
    commitment.save(update_fields=["status", "updated_at"])
    review_status = ReviewStatus.PENDING
    if commitment.action.verification_mode == VerificationMode.NO_VERIFICATION:
        review_status = ReviewStatus.NOT_REQUIRED
    elif commitment.action.verification_mode == VerificationMode.SELF_REPORTED:
        review_status = ReviewStatus.NOT_REQUIRED
        commitment.status = CommitmentStatus.VERIFIED
        commitment.completed_at = timezone.now()
        commitment.save(update_fields=["status", "completed_at", "updated_at"])
    submission = CompletionSubmission.objects.create(
        commitment=commitment,
        participant_note=note.strip(),
        review_status=review_status,
    )
    return submission


@transaction.atomic
def verify_completion(*, commitment: Commitment, reviewer) -> Commitment:
    if commitment.action.creator_id != reviewer.pk:
        raise ProsocialActionError("Only the action creator can verify completion.")
    if commitment.participant_id == reviewer.pk:
        raise ProsocialActionError("You cannot verify your own completion.")
    validate_transition(commitment.status, CommitmentStatus.VERIFIED)
    submission = commitment.completion_submission
    submission.review_status = ReviewStatus.VERIFIED
    submission.reviewed_by = reviewer
    submission.reviewed_at = timezone.now()
    submission.save()
    commitment.status = CommitmentStatus.VERIFIED
    commitment.completed_at = timezone.now()
    commitment.save(update_fields=["status", "completed_at", "updated_at"])
    return commitment


@transaction.atomic
def reject_completion(*, commitment: Commitment, reviewer, note: str = "") -> Commitment:
    if commitment.action.creator_id != reviewer.pk:
        raise ProsocialActionError("Only the action creator can reject completion.")
    validate_transition(commitment.status, CommitmentStatus.REJECTED)
    submission = commitment.completion_submission
    submission.review_status = ReviewStatus.REJECTED
    submission.reviewer_note = note.strip()
    submission.reviewed_by = reviewer
    submission.reviewed_at = timezone.now()
    submission.save()
    commitment.status = CommitmentStatus.REJECTED
    commitment.save(update_fields=["status", "updated_at"])
    return commitment


@transaction.atomic
def invite_user(*, action: ActionOpportunity, inviter, invitee, message: str = "") -> ActionInvitation:
    if inviter.pk == invitee.pk:
        raise ProsocialActionError("You cannot invite yourself.")
    if is_blocked(user_a=inviter, user_b=invitee):
        raise ProsocialActionError("This invitation is not available.")
    if action.creator_id != inviter.pk:
        raise ProsocialActionError("Only the action creator can send invitations.")
    invitation, created = ActionInvitation.objects.get_or_create(
        action=action,
        inviter=inviter,
        invitee=invitee,
        status=InvitationStatus.PENDING,
        defaults={"message": message.strip()},
    )
    if not created:
        raise ProsocialActionError("A pending invitation already exists.")
    return invitation


@transaction.atomic
def accept_invitation(*, invitation: ActionInvitation, invitee) -> Commitment:
    if invitation.invitee_id != invitee.pk:
        raise ProsocialActionError("Not authorized.")
    if invitation.status != InvitationStatus.PENDING:
        raise ProsocialActionError("This invitation is no longer pending.")
    invitation.status = InvitationStatus.ACCEPTED
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["status", "responded_at", "updated_at"])
    return commit_to_action(action=invitation.action, participant=invitee)


@transaction.atomic
def decline_invitation(*, invitation: ActionInvitation, invitee) -> ActionInvitation:
    if invitation.invitee_id != invitee.pk:
        raise ProsocialActionError("Not authorized.")
    invitation.status = InvitationStatus.DECLINED
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["status", "responded_at", "updated_at"])
    return invitation


@transaction.atomic
def send_acknowledgement(*, commitment: Commitment, sender, message: str = "") -> ActionAcknowledgement:
    if commitment.status not in (CommitmentStatus.COMPLETION_SUBMITTED, CommitmentStatus.VERIFIED):
        raise ProsocialActionError("Acknowledgement is only available after completion.")
    recipient = commitment.participant
    ack, created = ActionAcknowledgement.objects.get_or_create(
        commitment=commitment,
        sender=sender,
        defaults={"recipient": recipient, "message": message.strip()},
    )
    if not created:
        raise ProsocialActionError("You have already acknowledged this commitment.")
    Notification.objects.create(
        recipient=recipient,
        actor=sender,
        kind=NotificationKind.THANK_YOU_RECEIVED,
        payload={"commitment_public_id": str(commitment.public_id), "message": message.strip()},
    )
    return ack


def generate_due_reminders(*, now=None) -> int:
    from apps.prosocial_actions.selectors import get_due_reminders

    count = 0
    for commitment in get_due_reminders(now=now):
        Notification.objects.create(
            recipient=commitment.participant,
            kind=NotificationKind.REPLY_RECEIVED,
            payload={
                "type": "commitment_reminder",
                "action_public_id": str(commitment.action.public_id),
                "commitment_public_id": str(commitment.public_id),
            },
        )
        commitment.reminder_dispatched_at = now or timezone.now()
        commitment.save(update_fields=["reminder_dispatched_at"])
        count += 1
    return count
