import pytest
from django.contrib.auth import get_user_model

from apps.engagement.models import Challenge, ChallengePeriod, RestModeSession
from apps.engagement.services import complete_challenge, is_in_rest_mode, start_rest_mode

User = get_user_model()


@pytest.mark.django_db
def test_complete_challenge(user):
    challenge = Challenge.objects.create(
        title="Help one person",
        description="Send a supportive reply",
        period=ChallengePeriod.DAILY,
        xp_reward=30,
    )
    progress = complete_challenge(user=user, challenge=challenge)
    assert progress.completed_at is not None


@pytest.mark.django_db
def test_rest_mode(user):
    start_rest_mode(user=user)
    assert is_in_rest_mode(user=user) is True
