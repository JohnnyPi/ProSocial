from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class XPSource(models.TextChoices):
    DIRECT_SUPPORT = "DIRECT_SUPPORT", "Direct support"
    DETAILED_GUIDANCE = "DETAILED_GUIDANCE", "Detailed guidance"
    CRISIS_SUPPORT = "CRISIS_SUPPORT", "Crisis support"
    KNOWLEDGE_TIP = "KNOWLEDGE_TIP", "Knowledge tip"
    TUTORIAL = "TUTORIAL", "Tutorial"
    WELCOME = "WELCOME", "Welcome newcomer"
    DAILY_CHALLENGE = "DAILY_CHALLENGE", "Daily challenge"
    GUILD_MISSION = "GUILD_MISSION", "Guild mission"
    REFLECTION = "REFLECTION", "Reflection journal"
    CLIP_BONUS = "CLIP_BONUS", "Clip bonus"
    COMMITMENT = "COMMITMENT", "Commitment completed"


XP_AMOUNTS = {
    XPSource.DIRECT_SUPPORT: 25,
    XPSource.DETAILED_GUIDANCE: 50,
    XPSource.CRISIS_SUPPORT: 90,
    XPSource.KNOWLEDGE_TIP: 20,
    XPSource.TUTORIAL: 75,
    XPSource.WELCOME: 15,
    XPSource.DAILY_CHALLENGE: 30,
    XPSource.GUILD_MISSION: 75,
    XPSource.REFLECTION: 20,
    XPSource.CLIP_BONUS: 25,
    XPSource.COMMITMENT: 40,
}


class LevelTier(models.TextChoices):
    HELPER_INITIATE = "HELPER_INITIATE", "Helper Initiate"
    COMMUNITY_SUPPORTER = "COMMUNITY_SUPPORTER", "Community Supporter"
    MENTOR = "MENTOR", "Mentor"
    COMMUNITY_LEADER = "COMMUNITY_LEADER", "Community Leader"


def level_to_tier(level: int) -> str:
    if level <= 10:
        return LevelTier.HELPER_INITIATE
    if level <= 25:
        return LevelTier.COMMUNITY_SUPPORTER
    if level <= 50:
        return LevelTier.MENTOR
    return LevelTier.COMMUNITY_LEADER


def xp_for_level(level: int) -> int:
    return level * 100


class UserGamificationProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gamification_profile"
    )
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    streak_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    grace_used_this_week = models.BooleanField(default=False)
    multiplier = models.FloatField(default=1.0)

    @property
    def tier(self) -> str:
        return level_to_tier(self.level)


class XPTransaction(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="xp_transactions"
    )
    source = models.CharField(max_length=32, choices=XPSource.choices)
    base_amount = models.PositiveIntegerField()
    multiplier_applied = models.FloatField(default=1.0)
    final_amount = models.PositiveIntegerField()
    metadata = models.JSONField(default=dict, blank=True)


class BadgeDefinition(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    tier = models.CharField(max_length=16, default="bronze")
    xp_threshold = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return self.name


class UserBadge(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges"
    )
    badge = models.ForeignKey(BadgeDefinition, on_delete=models.CASCADE, related_name="awarded_to")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "badge"], name="unique_user_badge"),
        ]


class Achievement(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="achievements"
    )
    slug = models.SlugField(max_length=64)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "slug"], name="unique_user_achievement"),
        ]
