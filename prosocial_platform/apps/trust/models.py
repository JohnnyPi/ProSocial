from django.conf import settings
from django.db import models

from apps.common.models import ReactionCategory, TimeStampedModel


class HelperStyle(models.TextChoices):
    EMPATHIZER = "EMPATHIZER", "Empathizer"
    SAGE = "SAGE", "Sage"
    BUILDER = "BUILDER", "Builder"
    GUIDE = "GUIDE", "Guide"
    CONNECTOR = "CONNECTOR", "Connector"


class ScoreVisibility(models.TextChoices):
    HIDDEN = "HIDDEN", "Hidden"
    RANGE = "RANGE", "Range only"
    EXACT = "EXACT", "Exact score"


class AuthStrength(models.TextChoices):
    BASIC = "BASIC", "Basic"
    MFA = "MFA", "MFA enabled"
    STRONG_MFA = "STRONG_MFA", "Strong MFA"


class UserTrustProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trust_profile"
    )
    helper_style = models.CharField(max_length=16, choices=HelperStyle.choices, blank=True)
    helper_style_completed_at = models.DateTimeField(null=True, blank=True)
    engagement_trust_score = models.FloatField(default=0.0)
    popularity_trust_score = models.FloatField(default=0.0)
    contribution_score = models.FloatField(default=0.0)
    score_visibility = models.CharField(
        max_length=16,
        choices=ScoreVisibility.choices,
        default=ScoreVisibility.HIDDEN,
    )
    auth_strength = models.CharField(
        max_length=16, choices=AuthStrength.choices, default=AuthStrength.BASIC
    )
    identity_verified = models.BooleanField(default=False)
    role_verified = models.BooleanField(default=False)
    behavior_score = models.FloatField(default=50.0)
    risk_flags = models.JSONField(default=list, blank=True)

    def contribution_range_label(self) -> str:
        score = self.contribution_score
        if score < 30:
            return "New contributor"
        if score < 50:
            return "Growing helper"
        if score < 70:
            return "Trusted contributor"
        if score < 85:
            return "Community pillar"
        return "Legendary steward"


class PeerRatingDimension(models.TextChoices):
    ESCALATORY = "ESCALATORY", "Escalatory"
    DISMISSIVE = "DISMISSIVE", "Dismissive"
    SPAMMY = "SPAMMY", "Spammy"


NEGATIVE_DIMENSIONS = frozenset(PeerRatingDimension)


class PeerRating(TimeStampedModel):
    rater = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="peer_ratings_given"
    )
    post = models.ForeignKey(
        "posts.Post", null=True, blank=True, on_delete=models.CASCADE, related_name="peer_ratings"
    )
    reply = models.ForeignKey(
        "interactions.Reply",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="peer_ratings",
    )
    dimension = models.CharField(max_length=16, choices=PeerRatingDimension.choices)
    is_positive = models.BooleanField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(post__isnull=False, reply__isnull=True)
                    | models.Q(post__isnull=True, reply__isnull=False)
                ),
                name="peer_rating_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=["rater", "post", "dimension"],
                condition=models.Q(post__isnull=False),
                name="unique_peer_rating_post",
            ),
            models.UniqueConstraint(
                fields=["rater", "reply", "dimension"],
                condition=models.Q(reply__isnull=False),
                name="unique_peer_rating_reply",
            ),
        ]


class TrustEventType(models.TextChoices):
    PEER_RATING_POSITIVE = "PEER_RATING_POSITIVE", "Positive peer rating"
    PEER_RATING_NEGATIVE = "PEER_RATING_NEGATIVE", "Negative peer rating"
    PROSOCIAL_REACTION = "PROSOCIAL_REACTION", "Prosocial reaction"
    COMMITMENT_VERIFIED = "COMMITMENT_VERIFIED", "Commitment verified"
    CLIP_BY_OTHER = "CLIP_BY_OTHER", "Content clipped by other"
    MODERATION_UPHELD = "MODERATION_UPHELD", "Report upheld"
    MODERATION_FRIVOLOUS = "MODERATION_FRIVOLOUS", "Frivolous report"
    APPEAL_REVERSAL = "APPEAL_REVERSAL", "Appeal reversal"


class TrustEvent(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trust_events"
    )
    event_type = models.CharField(max_length=32, choices=TrustEventType.choices)
    weight = models.FloatField(default=1.0)
    source_type = models.CharField(max_length=32, blank=True)
    source_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]


class DomainReputation(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="domain_reputations"
    )
    category = models.CharField(max_length=16, choices=ReactionCategory.choices)
    score = models.FloatField(default=0.0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "category"], name="unique_domain_reputation"),
        ]


class TrustCluster(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trust_cluster"
    )
    cluster_id = models.CharField(max_length=64)


class PrivilegeDefinition(TimeStampedModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    domain = models.CharField(max_length=32, blank=True)
    criteria = models.JSONField(default=dict, blank=True)


class UserPrivilege(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="privileges"
    )
    privilege = models.ForeignKey(
        PrivilegeDefinition, on_delete=models.CASCADE, related_name="granted_to"
    )
    domain_scope = models.CharField(max_length=64, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "privilege", "domain_scope"],
                name="unique_user_privilege_scope",
            ),
        ]
