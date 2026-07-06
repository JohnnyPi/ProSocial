import uuid

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class DonationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    REFUNDED = "REFUNDED", "Refunded"


class DonationCampaign(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=200)
    organization_name = models.CharField(max_length=200)
    description = models.TextField(max_length=2000, blank=True)
    goal_cents = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="donation_campaigns"
    )


class Donation(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="donations"
    )
    campaign = models.ForeignKey(
        DonationCampaign, on_delete=models.CASCADE, related_name="donations"
    )
    amount_cents = models.PositiveIntegerField()
    processing_fee_cents = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=16, choices=DonationStatus.choices, default=DonationStatus.PENDING
    )
    is_anonymous = models.BooleanField(default=True)


class SkillOffering(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skill_offerings"
    )
    skill_name = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)
    is_remote = models.BooleanField(default=True)


class Workshop(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workshops"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000)
    scheduled_at = models.DateTimeField()
    max_participants = models.PositiveIntegerField(default=20)


class DataExportRequest(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="data_exports"
    )
    status = models.CharField(max_length=16, default="PENDING")
    file_path = models.CharField(max_length=500, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
