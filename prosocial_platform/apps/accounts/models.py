import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedModel


class User(AbstractUser):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField("email address", unique=True)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower("email"),
                name="unique_user_email_ci",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username


class AccountDeletionRequest(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deletion_requests",
    )
    scheduled_for = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["scheduled_for", "processed_at"]),
        ]
        ordering = ["-created_at"]

    @property
    def is_pending(self) -> bool:
        return self.cancelled_at is None and self.processed_at is None

    def __str__(self) -> str:
        return f"Deletion request for user {self.user_id} ({self.scheduled_for:%Y-%m-%d})"
