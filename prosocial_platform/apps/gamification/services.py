from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.common.models import ActivityEventType
from apps.common.services import record_activity_event
from apps.gamification.models import (
    XP_AMOUNTS,
    Achievement,
    BadgeDefinition,
    UserBadge,
    UserGamificationProfile,
    XPTransaction,
    xp_for_level,
)


class GamificationError(Exception):
    pass


def get_or_create_gamification_profile(*, user) -> UserGamificationProfile:
    profile, _ = UserGamificationProfile.objects.get_or_create(user=user)
    return profile


def _update_streak(profile: UserGamificationProfile) -> None:
    today = timezone.localdate()
    if profile.last_activity_date == today:
        return
    if profile.last_activity_date == today - timedelta(days=1):
        profile.streak_days += 1
    elif profile.last_activity_date and profile.last_activity_date < today - timedelta(days=1):
        if profile.grace_used_this_week:
            profile.streak_days = 1
            profile.grace_used_this_week = False
        else:
            profile.grace_used_this_week = True
            profile.streak_days = max(1, profile.streak_days)
    else:
        profile.streak_days = 1
    profile.last_activity_date = today
    if profile.streak_days >= 30:
        profile.multiplier = 2.0
    elif profile.streak_days >= 14:
        profile.multiplier = 1.8
    elif profile.streak_days >= 7:
        profile.multiplier = 1.5
    elif profile.streak_days >= 3:
        profile.multiplier = 1.2
    else:
        profile.multiplier = 1.0
    profile.multiplier = min(4.0, profile.multiplier)


@transaction.atomic
def award_xp(*, user, source: str, metadata: dict | None = None) -> XPTransaction:
    base = XP_AMOUNTS.get(source, 10)
    profile = get_or_create_gamification_profile(user=user)
    _update_streak(profile)
    multiplier = min(4.0, profile.multiplier)
    final = int(base * multiplier)
    profile.total_xp += final
    while profile.total_xp >= xp_for_level(profile.level):
        profile.level += 1
    profile.save()
    txn = XPTransaction.objects.create(
        user=user,
        source=source,
        base_amount=base,
        multiplier_applied=multiplier,
        final_amount=final,
        metadata=metadata or {},
    )
    record_activity_event(
        event_type=ActivityEventType.XP_AWARDED,
        actor=user,
        metadata={"source": source, "amount": final},
    )
    _check_badges(user=user, profile=profile)
    return txn


def _check_badges(*, user, profile: UserGamificationProfile) -> None:
    for badge in BadgeDefinition.objects.filter(xp_threshold__lte=profile.total_xp):
        UserBadge.objects.get_or_create(user=user, badge=badge)


@transaction.atomic
def record_achievement(*, user, slug: str, title: str, description: str = "") -> Achievement:
    achievement, created = Achievement.objects.get_or_create(
        user=user,
        slug=slug,
        defaults={"title": title, "description": description},
    )
    return achievement
