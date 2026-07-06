from apps.gamification.models import UserGamificationProfile
from apps.gamification.services import get_or_create_gamification_profile


def get_gamification_profile(*, user) -> UserGamificationProfile:
    return get_or_create_gamification_profile(user=user)
