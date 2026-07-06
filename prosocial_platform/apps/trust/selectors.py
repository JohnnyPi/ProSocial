from apps.trust.models import UserTrustProfile
from apps.trust.services import get_or_create_trust_profile


def get_trust_profile_for_user(*, user) -> UserTrustProfile:
    return get_or_create_trust_profile(user=user)
