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
    header_image = models.ImageField(upload_to="profiles/headers/", blank=True)

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


class VerificationMethod(models.TextChoices):
    SELF_ASSERTED = "SELF_ASSERTED", "Self-asserted"
    ORG_ATTESTED = "ORG_ATTESTED", "Organization-attested"
    DOMAIN_VERIFIED = "DOMAIN_VERIFIED", "Domain-verified"
    PLATFORM_REVIEWED = "PLATFORM_REVIEWED", "Platform-reviewed"
    CREDENTIAL = "CREDENTIAL", "Credential-backed"


class EndorsementStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    VERIFIED = "VERIFIED", "Verified"
    REJECTED = "REJECTED", "Rejected"


class ScopedEndorsement(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="endorsements"
    )
    claim_type = models.CharField(max_length=64)
    claim_label = models.CharField(max_length=200)
    verification_method = models.CharField(max_length=24, choices=VerificationMethod.choices)
    issuer = models.CharField(max_length=200, blank=True)
    scope = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=16,
        choices=EndorsementStatus.choices,
        default=EndorsementStatus.PENDING,
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]
