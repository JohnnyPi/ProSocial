from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Profile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    handle = models.CharField(max_length=30, unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    biography = models.TextField(max_length=500, blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower("handle"),
                name="unique_profile_handle_ci",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.handle:
            self.handle = self.handle.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.handle

    @property
    def public_display_name(self) -> str:
        return self.display_name or self.handle
