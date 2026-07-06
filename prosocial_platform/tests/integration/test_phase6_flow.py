import pytest
from django.contrib.auth import get_user_model

from apps.gamification.models import XPTransaction
from apps.gamification.services import award_xp, get_or_create_gamification_profile

User = get_user_model()


@pytest.mark.django_db
def test_award_xp(user):
    txn = award_xp(user=user, source="DIRECT_SUPPORT")
    assert txn.final_amount >= 25
    profile = get_or_create_gamification_profile(user=user)
    assert profile.total_xp >= 25


@pytest.mark.django_db
def test_xp_transaction_recorded(user):
    award_xp(user=user, source="WELCOME")
    assert XPTransaction.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_level_increases_with_xp(user):
    profile = get_or_create_gamification_profile(user=user)
    for _ in range(5):
        award_xp(user=user, source="TUTORIAL")
    profile.refresh_from_db()
    assert profile.level >= 1
    assert profile.total_xp > 0
