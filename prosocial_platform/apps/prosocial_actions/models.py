import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import TimeStampedModel


class ActionStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    FULL = "FULL", "Full"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    EXPIRED = "EXPIRED", "Expired"


class VerificationMode(models.TextChoices):
    SELF_REPORTED = "SELF_REPORTED", "Self reported"
    CREATOR_CONFIRMED = "CREATOR_CONFIRMED", "Creator confirmed"
    RECIPIENT_CONFIRMED = "RECIPIENT_CONFIRMED", "Recipient confirmed"
    NO_VERIFICATION = "NO_VERIFICATION", "No verification"


class ActionOpportunity(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    post = models.OneToOneField(
        "posts.Post", on_delete=models.CASCADE, related_name="action_opportunity"
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_actions",
    )
    status = models.CharField(
        max_length=16, choices=ActionStatus.choices, default=ActionStatus.OPEN
    )
    location_label = models.CharField(max_length=200, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    verification_mode = models.CharField(
        max_length=24,
        choices=VerificationMode.choices,
        default=VerificationMode.SELF_REPORTED,
    )
    completion_instructions = models.TextField(max_length=1000, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "starts_at"]),
        ]

    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            raise ValidationError("End time cannot precede start time.")
        if self.capacity is not None and self.capacity < 1:
            raise ValidationError("Capacity must be positive when supplied.")

    @property
    def accepts_commitments(self) -> bool:
        return self.status in (ActionStatus.OPEN, ActionStatus.FULL)


class CommitmentStatus(models.TextChoices):
    SAVED = "SAVED", "Saved"
    COMMITTED = "COMMITTED", "Committed"
    COMPLETION_SUBMITTED = "COMPLETION_SUBMITTED", "Completion submitted"
    VERIFIED = "VERIFIED", "Verified"
    REJECTED = "REJECTED", "Rejected"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"
    EXPIRED = "EXPIRED", "Expired"


ACTIVE_COMMITMENT_STATUSES = {
    CommitmentStatus.SAVED,
    CommitmentStatus.COMMITTED,
    CommitmentStatus.COMPLETION_SUBMITTED,
}


class Commitment(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    action = models.ForeignKey(
        ActionOpportunity, on_delete=models.CASCADE, related_name="commitments"
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commitments",
    )
    status = models.CharField(
        max_length=24, choices=CommitmentStatus.choices, default=CommitmentStatus.SAVED
    )
    scheduled_for = models.DateTimeField(null=True, blank=True)
    reminder_at = models.DateTimeField(null=True, blank=True)
    reminder_dispatched_at = models.DateTimeField(null=True, blank=True)
    reminders_enabled = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    private_note = models.TextField(max_length=500, blank=True)
    committed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["participant", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["action", "participant"],
                condition=models.Q(
                    status__in=["SAVED", "COMMITTED", "COMPLETION_SUBMITTED"]
                ),
                name="unique_active_commitment_per_action",
            ),
        ]


class ReviewStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    VERIFIED = "VERIFIED", "Verified"
    REJECTED = "REJECTED", "Rejected"
    NOT_REQUIRED = "NOT_REQUIRED", "Not required"


class CompletionSubmission(models.Model):
    commitment = models.OneToOneField(
        Commitment, on_delete=models.CASCADE, related_name="completion_submission"
    )
    participant_note = models.TextField(max_length=1000, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="completion_reviews",
    )
    review_status = models.CharField(
        max_length=16, choices=ReviewStatus.choices, default=ReviewStatus.PENDING
    )
    reviewer_note = models.TextField(max_length=500, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)


class InvitationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    DECLINED = "DECLINED", "Declined"
    CANCELLED = "CANCELLED", "Cancelled"
    EXPIRED = "EXPIRED", "Expired"


class ActionInvitation(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    action = models.ForeignKey(
        ActionOpportunity, on_delete=models.CASCADE, related_name="invitations"
    )
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invitations_sent"
    )
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invitations_received"
    )
    status = models.CharField(
        max_length=16, choices=InvitationStatus.choices, default=InvitationStatus.PENDING
    )
    message = models.CharField(max_length=280, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["action", "inviter", "invitee"],
                condition=models.Q(status="PENDING"),
                name="unique_pending_invitation",
            ),
        ]


class ActionAcknowledgement(models.Model):
    commitment = models.ForeignKey(
        Commitment, on_delete=models.CASCADE, related_name="acknowledgements"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="acknowledgements_sent"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="acknowledgements_received"
    )
    message = models.CharField(max_length=280, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["commitment", "sender"], name="unique_acknowledgement_per_sender"
            ),
        ]
