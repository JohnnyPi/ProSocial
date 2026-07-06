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
    PlatformRole.AMBASSADOR: (85, 80),
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
        "posts.Post", null=True, blank=True, on_delete=models.CASCADE, related_name="moderation_reviews"
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


class TransparencyLogEntry(TimeStampedModel):
    action_type = models.CharField(max_length=64)
    summary = models.TextField(max_length=1000)
    anonymized_actor_id = models.CharField(max_length=64, blank=True)


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
