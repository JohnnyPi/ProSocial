"""Anti-brigading and reputation-gaming signal weighting."""

import math
from datetime import timedelta

from django.utils import timezone

from apps.interactions.models import ProsocialReaction
from apps.trust.clusters import get_cluster_ids_for_users
from apps.trust.models import PeerRating, TrustEvent

CLUSTER_CONCENTRATION_THRESHOLD = 0.5
VELOCITY_WINDOW_MINUTES = 30
VELOCITY_SPIKE_COUNT = 10
RECIPROCAL_LOOKBACK_DAYS = 30
DECAY_HALF_LIFE_DAYS = 90


def _rater_cluster_concentration(*, target_user, new_rater, post=None, reply=None) -> float:
    """Return fraction of recent raters sharing new_rater's cluster."""
    rater_ids: list[int] = []
    if post:
        rater_ids = list(
            ProsocialReaction.objects.filter(post=post)
            .order_by("-created_at")[:20]
            .values_list("sender_id", flat=True)
        )
        rater_ids += list(
            PeerRating.objects.filter(post=post)
            .order_by("-created_at")[:20]
            .values_list("rater_id", flat=True)
        )
    elif reply:
        rater_ids = list(
            ProsocialReaction.objects.filter(reply=reply)
            .order_by("-created_at")[:20]
            .values_list("sender_id", flat=True)
        )
        rater_ids += list(
            PeerRating.objects.filter(reply=reply)
            .order_by("-created_at")[:20]
            .values_list("rater_id", flat=True)
        )
    if not rater_ids:
        return 0.0
    unique_rater_ids = set(rater_ids)
    cluster_map = get_cluster_ids_for_users(user_ids=unique_rater_ids | {new_rater.pk})
    new_cluster = cluster_map[new_rater.pk]
    same_cluster = sum(1 for rid in unique_rater_ids if cluster_map[rid] == new_cluster)
    return same_cluster / len(unique_rater_ids)


def _velocity_multiplier(*, target_user) -> float:
    cutoff = timezone.now() - timedelta(minutes=VELOCITY_WINDOW_MINUTES)
    recent_negative = TrustEvent.objects.filter(
        user=target_user,
        weight__lt=0,
        created_at__gte=cutoff,
    ).count()
    if recent_negative >= VELOCITY_SPIKE_COUNT:
        return 0.25
    return 1.0


def _reciprocal_penalty(*, rater, target_user) -> float:
    cutoff = timezone.now() - timedelta(days=RECIPROCAL_LOOKBACK_DAYS)
    reciprocal = TrustEvent.objects.filter(
        user=rater,
        source_type="user",
        source_id=str(target_user.pk),
        created_at__gte=cutoff,
    ).exists()
    return 0.5 if reciprocal else 1.0


def _account_age_multiplier(*, rater) -> float:
    age_days = (timezone.now() - rater.date_joined).days
    if age_days < 7:
        return 0.5
    if age_days < 30:
        return 0.75
    return 1.0


def apply_time_decay(*, weight: float, created_at) -> float:
    age_days = (timezone.now() - created_at).total_seconds() / 86400
    return weight * math.exp(-age_days / DECAY_HALF_LIFE_DAYS)


def compute_effective_weight(
    *,
    base_weight: float,
    rater,
    target_user,
    post=None,
    reply=None,
) -> float:
    weight = base_weight
    concentration = _rater_cluster_concentration(
        target_user=target_user, new_rater=rater, post=post, reply=reply
    )
    if concentration > CLUSTER_CONCENTRATION_THRESHOLD:
        weight *= 0.5
    weight *= _velocity_multiplier(target_user=target_user)
    weight *= _reciprocal_penalty(rater=rater, target_user=target_user)
    weight *= _account_age_multiplier(rater=rater)
    return round(weight, 3)


def brigading_score(*, target_user) -> float:
    """Higher score means more likely coordinated negative action."""
    cutoff = timezone.now() - timedelta(minutes=VELOCITY_WINDOW_MINUTES)
    events = TrustEvent.objects.filter(user=target_user, weight__lt=0, created_at__gte=cutoff)
    if not events.exists():
        return 0.0
    velocity = events.count() / VELOCITY_SPIKE_COUNT
    return min(1.0, velocity)
