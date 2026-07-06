import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel


class ReplyQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(deleted_at__isnull=True)


class Reply(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="replies"
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    body = models.TextField(max_length=2000)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ReplyQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["author", "created_at"]),
        ]
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Reply by {self.author_id} on post {self.post_id}"

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])


class ThankYou(TimeStampedModel):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="thank_yous_sent"
    )
    post = models.ForeignKey(
        "posts.Post", null=True, blank=True, on_delete=models.CASCADE, related_name="thank_yous"
    )
    reply = models.ForeignKey(
        Reply, null=True, blank=True, on_delete=models.CASCADE, related_name="thank_yous"
    )
    optional_note = models.CharField(max_length=280, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(post__isnull=False, reply__isnull=True)
                    | models.Q(post__isnull=True, reply__isnull=False)
                ),
                name="thank_you_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=["sender", "post"],
                condition=models.Q(post__isnull=False),
                name="unique_thank_you_per_post",
            ),
            models.UniqueConstraint(
                fields=["sender", "reply"],
                condition=models.Q(reply__isnull=False),
                name="unique_thank_you_per_reply",
            ),
        ]


class NotificationKind(models.TextChoices):
    REPLY_RECEIVED = "REPLY_RECEIVED", "Reply received"
    REPLY_TO_REPLY = "REPLY_TO_REPLY", "Reply to reply"
    THANK_YOU_RECEIVED = "THANK_YOU_RECEIVED", "Thank you received"
    REPORT_RESOLVED = "REPORT_RESOLVED", "Report resolved"
    USER_FOLLOWED = "USER_FOLLOWED", "User followed"
    POST_FOLLOWED = "POST_FOLLOWED", "Post followed"
    MESSAGE_RECEIVED = "MESSAGE_RECEIVED", "Message received"
    GUILD_INVITE = "GUILD_INVITE", "Guild invite"
    CHALLENGE_COMPLETED = "CHALLENGE_COMPLETED", "Challenge completed"
    XP_EARNED = "XP_EARNED", "XP earned"
    MODERATION_ACTION = "MODERATION_ACTION", "Moderation action"
    CRISIS_REVIEW = "CRISIS_REVIEW", "Crisis review"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notifications_sent",
    )
    kind = models.CharField(max_length=32, choices=NotificationKind.choices)
    post = models.ForeignKey(
        "posts.Post", null=True, blank=True, on_delete=models.CASCADE, related_name="notifications"
    )
    reply = models.ForeignKey(
        Reply, null=True, blank=True, on_delete=models.CASCADE, related_name="notifications"
    )
    thank_you = models.ForeignKey(
        ThankYou, null=True, blank=True, on_delete=models.CASCADE, related_name="notifications"
    )
    payload = models.JSONField(default=dict, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class HiddenPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hidden_posts"
    )
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="hidden_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_hidden_post"),
        ]


class UserMute(models.Model):
    muting_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mutes_created"
    )
    muted_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="muted_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["muting_user", "muted_user"], name="unique_user_mute"
            ),
        ]


class UserBlock(models.Model):
    blocking_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blocks_created"
    )
    blocked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blocked_by"
    )
    optional_reason_code = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["blocking_user", "blocked_user"], name="unique_user_block"
            ),
        ]


class ReportReason(models.TextChoices):
    HARASSMENT = "HARASSMENT", "Harassment"
    THREAT = "THREAT", "Threat"
    HATE_OR_DEHUMANIZATION = "HATE_OR_DEHUMANIZATION", "Hate or dehumanization"
    SPAM = "SPAM", "Spam"
    IMPERSONATION = "IMPERSONATION", "Impersonation"
    PRIVACY = "PRIVACY", "Privacy"
    COORDINATED_ABUSE = "COORDINATED_ABUSE", "Coordinated abuse"
    OTHER = "OTHER", "Other"


class ReportStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    IN_REVIEW = "IN_REVIEW", "In review"
    RESOLVED_ACTIONED = "RESOLVED_ACTIONED", "Resolved — actioned"
    RESOLVED_NO_ACTION = "RESOLVED_NO_ACTION", "Resolved — no action"
    DUPLICATE = "DUPLICATE", "Duplicate"


class ContentReport(models.Model):
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_reports",
    )
    post = models.ForeignKey(
        "posts.Post", null=True, blank=True, on_delete=models.CASCADE, related_name="reports"
    )
    reply = models.ForeignKey(
        Reply, null=True, blank=True, on_delete=models.CASCADE, related_name="reports"
    )
    reason = models.CharField(max_length=32, choices=ReportReason.choices)
    details = models.TextField(max_length=1000, blank=True)
    status = models.CharField(
        max_length=24, choices=ReportStatus.choices, default=ReportStatus.OPEN
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_reports",
    )
    resolution_note = models.TextField(max_length=1000, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(post__isnull=False, reply__isnull=True)
                    | models.Q(post__isnull=True, reply__isnull=False)
                ),
                name="report_exactly_one_target",
            ),
        ]


class ProsocialReactionKind(models.TextChoices):
    CONSTRUCTIVE = "CONSTRUCTIVE", "Constructive"
    SUPPORTIVE = "SUPPORTIVE", "Supportive"
    INSIGHTFUL = "INSIGHTFUL", "Insightful"


class ProsocialReaction(TimeStampedModel):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prosocial_reactions_sent",
    )
    post = models.ForeignKey(
        "posts.Post", null=True, blank=True, on_delete=models.CASCADE, related_name="prosocial_reactions"
    )
    reply = models.ForeignKey(
        Reply, null=True, blank=True, on_delete=models.CASCADE, related_name="prosocial_reactions"
    )
    kind = models.CharField(max_length=16, choices=ProsocialReactionKind.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(post__isnull=False, reply__isnull=True)
                    | models.Q(post__isnull=True, reply__isnull=False)
                ),
                name="prosocial_reaction_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=["sender", "post", "kind"],
                condition=models.Q(post__isnull=False),
                name="unique_prosocial_reaction_post",
            ),
            models.UniqueConstraint(
                fields=["sender", "reply", "kind"],
                condition=models.Q(reply__isnull=False),
                name="unique_prosocial_reaction_reply",
            ),
        ]
