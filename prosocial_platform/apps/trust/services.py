from django.db import transaction
from django.utils import timezone

from apps.common.models import ActivityEventType
from apps.common.services import record_activity_event
from apps.trust.models import (
    POSITIVE_DIMENSIONS,
    PeerRating,
    PeerRatingDimension,
    TrustEvent,
    TrustEventType,
    UserTrustProfile,
)


class TrustError(Exception):
    pass


def get_or_create_trust_profile(*, user) -> UserTrustProfile:
    profile, _ = UserTrustProfile.objects.get_or_create(user=user)
    return profile


@transaction.atomic
def set_helper_style(*, user, helper_style: str) -> UserTrustProfile:
    profile = get_or_create_trust_profile(user=user)
    profile.helper_style = helper_style
    profile.helper_style_completed_at = timezone.now()
    profile.save(update_fields=["helper_style", "helper_style_completed_at", "updated_at"])
    return profile


@transaction.atomic
def create_peer_rating(*, rater, post=None, reply=None, dimension: str) -> PeerRating:
    if rater.pk == (reply.author_id if reply else post.author_id):
        raise TrustError("You cannot rate your own content.")
    is_positive = dimension in {d.value for d in POSITIVE_DIMENSIONS}
    rating, created = PeerRating.objects.get_or_create(
        rater=rater,
        post=post,
        reply=reply,
        dimension=dimension,
        defaults={"is_positive": is_positive},
    )
    if not created:
        raise TrustError("You already rated this content.")
    subject = reply.author if reply else post.author
    TrustEvent.objects.create(
        user=subject,
        event_type=TrustEventType.PEER_RATING_POSITIVE if is_positive else TrustEventType.PEER_RATING_NEGATIVE,
        weight=2.0 if is_positive else -1.0,
        source_type="reply" if reply else "post",
        source_id=str(reply.pk if reply else post.pk),
    )
    record_activity_event(
        event_type=ActivityEventType.PEER_RATING_GIVEN,
        actor=rater,
        metadata={"dimension": dimension, "positive": is_positive},
    )
    recalculate_trust_scores(user=subject)
    return rating


def recalculate_trust_scores(*, user) -> UserTrustProfile:
    profile = get_or_create_trust_profile(user=user)
    events = TrustEvent.objects.filter(user=user).order_by("-created_at")[:200]
    positive_weight = sum(e.weight for e in events if e.weight > 0)
    negative_weight = abs(sum(e.weight for e in events if e.weight < 0))
    ets = min(100.0, max(0.0, 40.0 + positive_weight * 2.0 - negative_weight * 3.0))
    from apps.follows.models import UserFollow
    from apps.knowledge.models import Clip

    followers = UserFollow.objects.filter(following=user).count()
    clips_by_others = Clip.objects.filter(post__author=user).exclude(owner=user).count()
    pts = min(100.0, max(0.0, followers * 2.0 + clips_by_others * 3.0))
    contribution = (ets * 0.65) + (pts * 0.35)
    profile.engagement_trust_score = round(ets, 2)
    profile.popularity_trust_score = round(pts, 2)
    profile.contribution_score = round(contribution, 2)
    profile.save(
        update_fields=[
            "engagement_trust_score",
            "popularity_trust_score",
            "contribution_score",
            "updated_at",
        ]
    )
    record_activity_event(
        event_type=ActivityEventType.TRUST_SCORE_UPDATED,
        actor=user,
        metadata={"ets": ets, "pts": pts, "contribution": contribution},
    )
    from apps.moderation.services import sync_user_role

    sync_user_role(user=user)
    return profile


def ets_meets_threshold(*, user, threshold: float) -> bool:
    profile = get_or_create_trust_profile(user=user)
    return profile.engagement_trust_score >= threshold


def role_eligible(*, user, ets_min: float, contribution_min: float) -> bool:
    profile = get_or_create_trust_profile(user=user)
    if profile.engagement_trust_score < ets_min:
        return False
    return profile.contribution_score >= contribution_min
