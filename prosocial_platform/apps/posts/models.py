import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel


class ModerationStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    HIDDEN = "HIDDEN", "Hidden"
    REMOVED = "REMOVED", "Removed"


class PostKind(models.TextChoices):
    GENERAL = "GENERAL", "General"
    HELP_REQUEST = "HELP_REQUEST", "Help request"
    HELP_OFFER = "HELP_OFFER", "Help offer"
    ENCOURAGEMENT_REQUEST = "ENCOURAGEMENT_REQUEST", "Encouragement request"
    LOCAL_ACTION = "LOCAL_ACTION", "Local action"
    VOLUNTEER_OPPORTUNITY = "VOLUNTEER_OPPORTUNITY", "Volunteer opportunity"


class ThreadType(models.TextChoices):
    DISCUSSION = "DISCUSSION", "Discussion"
    HELP_REQUEST = "HELP_REQUEST", "Help request"
    KNOWLEDGE_SHARE = "KNOWLEDGE_SHARE", "Knowledge share"
    SUPPORT_CIRCLE = "SUPPORT_CIRCLE", "Support circle"
    CHALLENGE = "CHALLENGE", "Challenge"


class PostQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(deleted_at__isnull=True, moderation_status=ModerationStatus.ACTIVE)


class Post(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    kind = models.CharField(
        max_length=32,
        choices=PostKind.choices,
        default=PostKind.GENERAL,
    )
    thread_type = models.CharField(
        max_length=32,
        choices=ThreadType.choices,
        default=ThreadType.DISCUSSION,
    )
    title = models.CharField(max_length=200, blank=True)
    guild = models.ForeignKey(
        "guilds.Guild",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="posts",
    )
    body = models.TextField(blank=True, max_length=5000)
    image = models.ImageField(upload_to="posts/", blank=True)
    image_alt_text = models.CharField(max_length=255, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    moderation_status = models.CharField(
        max_length=16,
        choices=ModerationStatus.choices,
        default=ModerationStatus.ACTIVE,
    )

    objects = PostQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["moderation_status", "created_at"]),
            models.Index(fields=["kind", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        preview = (self.body[:50] + "…") if len(self.body) > 50 else self.body
        return preview or f"Post {self.public_id}"

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def clean(self):
        from django.core.exceptions import ValidationError

        body = (self.body or "").strip()
        has_image = bool(self.image)
        if not body and not has_image:
            raise ValidationError("A post must contain text, an image, or both.")

    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])
