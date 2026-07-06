from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class PlatformRole(models.TextChoices):
    NEW_MEMBER = "NEW_MEMBER", "New member"
    MEMBER = "MEMBER", "Member"
    COMMUNITY_SUPPORTER = "COMMUNITY_SUPPORTER", "Community supporter"
    MENTOR = "MENTOR", "Mentor"
    COMMUNITY_GUIDE = "COMMUNITY_GUIDE", "Community guide"
    AMBASSADOR = "AMBASSADOR", "Ambassador"
    MODERATOR = "MODERATOR", "Moderator"
    COMMUNITY_LEADER = "COMMUNITY_LEADER", "Community leader"
    LEGENDARY_STEWARD = "LEGENDARY_STEWARD", "Legendary steward"


ROLE_THRESHOLDS = {
    PlatformRole.MEMBER: (40, 30),
    PlatformRole.COMMUNITY_SUPPORTER: (60, 50),
    PlatformRole.MENTOR: (75, 70),
    PlatformRole.COMMUNITY_GUIDE: (80, 75),
    PlatformRole.AMBASSADOR: (88, 82),
    PlatformRole.MODERATOR: (85, 80),
    PlatformRole.COMMUNITY_LEADER: (90, 90),
}


class UserRoleAssignment(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="role_assignments"
    )
    role = models.CharField(max_length=32, choices=PlatformRole.choices)
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class ModerationReviewStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    EDIT_REQUIRED = "EDIT_REQUIRED", "Edit required"
    REMOVED = "REMOVED", "Removed"
    ESCALATED = "ESCALATED", "Escalated"


class ModerationReview(TimeStampedModel):
    content_report = models.ForeignKey(
        "interactions.ContentReport",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderation_reviews",
    )
    post = models.ForeignKey(
        "posts.Post",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="moderation_reviews",
    )
    reply = models.ForeignKey(
        "interactions.Reply",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="moderation_reviews",
    )
    ai_sentiment_label = models.CharField(max_length=16, blank=True)
    status = models.CharField(
        max_length=16,
        choices=ModerationReviewStatus.choices,
        default=ModerationReviewStatus.PENDING,
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderation_reviews_done",
    )
    explanation = models.TextField(max_length=2000, blank=True)
    is_high_priority = models.BooleanField(default=False)


class TransparencyLogEntry(TimeStampedModel):
    action_type = models.CharField(max_length=64)
    summary = models.TextField(max_length=1000)
    anonymized_actor_id = models.CharField(max_length=64, blank=True)


class ModerationActionType(models.TextChoices):
    REMOVED = "REMOVED", "Removed"
    LIMITED = "LIMITED", "Limited"
    DOWNRANKED = "DOWNRANKED", "Downranked"
    WARNING = "WARNING", "Warning"


class ModerationActionSource(models.TextChoices):
    AUTOMATED = "AUTOMATED", "Automated"
    USER_REPORT = "USER_REPORT", "User report"
    MODERATOR = "MODERATOR", "Moderator"
    STAFF = "STAFF", "Staff"


class ModerationAction(TimeStampedModel):
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="moderation_actions"
    )
    post = models.ForeignKey(
        "posts.Post",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="moderation_actions",
    )
    reply = models.ForeignKey(
        "interactions.Reply",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="moderation_actions",
    )
    moderation_review = models.ForeignKey(
        ModerationReview,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="actions",
    )
    action_type = models.CharField(max_length=16, choices=ModerationActionType.choices)
    source = models.CharField(max_length=16, choices=ModerationActionSource.choices)
    rule_code = models.CharField(max_length=32)
    explanation = models.TextField(max_length=2000)
    is_reversed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["target_user", "created_at"]),
            models.Index(fields=["rule_code", "is_reversed"]),
        ]


class AppealStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    DENIED = "DENIED", "Denied"


class Appeal(TimeStampedModel):
    moderation_action = models.ForeignKey(
        ModerationAction, on_delete=models.CASCADE, related_name="appeals"
    )
    appellant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appeals"
    )
    statement = models.TextField(max_length=2000)
    status = models.CharField(
        max_length=16, choices=AppealStatus.choices, default=AppealStatus.PENDING
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="appeals_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    outcome_note = models.TextField(max_length=2000, blank=True)


class AppealOutcome(TimeStampedModel):
    appeal = models.OneToOneField(Appeal, on_delete=models.CASCADE, related_name="outcome")
    reversed_action = models.BooleanField(default=False)
    reputation_restored = models.BooleanField(default=False)


class CrisisFlag(TimeStampedModel):
    post = models.ForeignKey(
        "posts.Post", null=True, blank=True, on_delete=models.CASCADE, related_name="crisis_flags"
    )
    reply = models.ForeignKey(
        "interactions.Reply",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="crisis_flags",
    )
    detected_phrase = models.CharField(max_length=200, blank=True)
    resources_shown = models.BooleanField(default=False)
    moderator_notified = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
