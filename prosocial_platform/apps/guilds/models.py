import uuid

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class GuildType(models.TextChoices):
    CAUSE = "CAUSE", "Cause"
    HOBBY = "HOBBY", "Hobby"
    HELPER_STYLE = "HELPER_STYLE", "Helper style"
    FORUM_THEME = "FORUM_THEME", "Forum theme"


FORUM_THEME_PRESETS = (
    ("local-initiatives", "Local Initiatives"),
    ("mental-wellness", "Mental Wellness"),
    ("skill-sharing", "Skill-Sharing"),
    ("environmental-action", "Environmental Action"),
)


class GuildRole(models.TextChoices):
    LEADER = "LEADER", "Leader"
    MEMBER = "MEMBER", "Member"


class Guild(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=2000, blank=True)
    guild_type = models.CharField(max_length=16, choices=GuildType.choices, default=GuildType.CAUSE)
    banner_url = models.URLField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="guilds_created"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class GuildMembership(models.Model):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="guild_memberships"
    )
    role = models.CharField(max_length=16, choices=GuildRole.choices, default=GuildRole.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["guild", "user"], name="unique_guild_membership"),
        ]
