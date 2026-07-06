from django.db import transaction
from django.utils import timezone

from apps.engagement.models import Challenge, RestModeSession, UserChallengeProgress
from apps.gamification.models import XPSource
from apps.gamification.services import award_xp


@transaction.atomic
def complete_challenge(*, user, challenge: Challenge) -> UserChallengeProgress:
    progress, _ = UserChallengeProgress.objects.get_or_create(user=user, challenge=challenge)
    if progress.completed_at:
        return progress
    progress.completed_at = timezone.now()
    progress.save(update_fields=["completed_at", "updated_at"])
    award_xp(user=user, source=XPSource.DAILY_CHALLENGE, metadata={"challenge_id": challenge.pk})
    return progress


@transaction.atomic
def start_rest_mode(*, user) -> RestModeSession:
    RestModeSession.objects.filter(user=user, ended_at__isnull=True).update(ended_at=timezone.now())
    return RestModeSession.objects.create(user=user)


@transaction.atomic
def end_rest_mode(*, user) -> None:
    RestModeSession.objects.filter(user=user, ended_at__isnull=True).update(ended_at=timezone.now())


def is_in_rest_mode(*, user) -> bool:
    return RestModeSession.objects.filter(user=user, ended_at__isnull=True).exists()
