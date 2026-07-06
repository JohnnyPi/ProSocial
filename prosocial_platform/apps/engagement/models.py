from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class ChallengePeriod(models.TextChoices):
    DAILY = "DAILY", "Daily"
    WEEKLY = "WEEKLY", "Weekly"
    SEASONAL = "SEASONAL", "Seasonal"


class Challenge(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    period = models.CharField(max_length=16, choices=ChallengePeriod.choices)
    xp_reward = models.PositiveIntegerField(default=30)
    helper_style = models.CharField(max_length=16, blank=True)
    is_active = models.BooleanField(default=True)


class UserChallengeProgress(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="challenge_progress"
    )
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="progress")
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "challenge"], name="unique_user_challenge"),
        ]


class GuildMission(TimeStampedModel):
    guild = models.ForeignKey("guilds.Guild", on_delete=models.CASCADE, related_name="missions")
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    target_count = models.PositiveIntegerField(default=10)
    current_count = models.PositiveIntegerField(default=0)
    xp_reward = models.PositiveIntegerField(default=75)
    is_active = models.BooleanField(default=True)


class RestModeSession(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rest_sessions"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    mute_notifications = models.BooleanField(default=True)


class ReEngagementMessage(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reengagement_messages"
    )
    day_threshold = models.PositiveIntegerField()
    message_text = models.TextField(max_length=1000)
    sent_at = models.DateTimeField(auto_now_add=True)
