from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActivityEventType(models.TextChoices):
    ACCOUNT_REGISTERED = "ACCOUNT_REGISTERED", "Account registered"
    ACCOUNT_DELETION_REQUESTED = "ACCOUNT_DELETION_REQUESTED", "Account deletion requested"
    ACCOUNT_DELETION_CANCELLED = "ACCOUNT_DELETION_CANCELLED", "Account deletion cancelled"
    ACCOUNT_DELETED = "ACCOUNT_DELETED", "Account deleted"
    LOGIN_SUCCEEDED = "LOGIN_SUCCEEDED", "Login succeeded"
    LOGIN_FAILED = "LOGIN_FAILED", "Login failed"
    PROFILE_UPDATED = "PROFILE_UPDATED", "Profile updated"
    POST_CREATED = "POST_CREATED", "Post created"
    POST_UPDATED = "POST_UPDATED", "Post updated"
    POST_DELETED = "POST_DELETED", "Post deleted"
    IMAGE_UPLOAD_REJECTED = "IMAGE_UPLOAD_REJECTED", "Image upload rejected"
    CLIP_CREATED = "CLIP_CREATED", "Clip created"
    COLLECTION_CREATED = "COLLECTION_CREATED", "Collection created"
    USER_FOLLOWED = "USER_FOLLOWED", "User followed"
    POST_FOLLOWED = "POST_FOLLOWED", "Post followed"
    GUILD_JOINED = "GUILD_JOINED", "Guild joined"
    MESSAGE_SENT = "MESSAGE_SENT", "Message sent"
    PEER_RATING_GIVEN = "PEER_RATING_GIVEN", "Peer rating given"
    XP_AWARDED = "XP_AWARDED", "XP awarded"
    TRUST_SCORE_UPDATED = "TRUST_SCORE_UPDATED", "Trust score updated"


class ActivityEvent(TimeStampedModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activity_events",
    )
    event_type = models.CharField(max_length=64, choices=ActivityEventType.choices)
    object_type = models.CharField(max_length=64, blank=True)
    object_public_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.event_type} ({self.created_at:%Y-%m-%d %H:%M})"
