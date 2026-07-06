"""Capability registry for progressive account trust.

Access control uses three layers (do not add a fourth without explicit design):

- **Capabilities** (this module): assurance floors — auth strength, behavior_score,
  identity_verified, role_verified. Example: ``submit_context_notes`` requires
  behavior_score >= 40.
- **Earned privileges** (``trust.services`` / ``UserPrivilege``): domain reputation
  thresholds. Example: ``can_tag_posts`` requires knowledge domain score >= 20.
- **Platform roles** (``moderation.models`` / ``UserRoleAssignment``): auto-assigned
  stewardship tiers from contribution scores. Example: moderator queue access uses
  ``PlatformRole.MODERATOR``, not the ``moderate`` capability here.
"""

from django.conf import settings

from apps.trust.models import AuthStrength, UserTrustProfile
from apps.trust.services import get_or_create_trust_profile


class CapabilityError(Exception):
    pass


CAPABILITIES = {
    "post": {"auth_strength": AuthStrength.BASIC},
    "receive_tips": {"identity_verified": True},
    "moderate": {"auth_strength": AuthStrength.MFA, "behavior_score_min": 60},
    "claim_official_role": {"role_verified": True},
    "submit_context_notes": {"behavior_score_min": 40},
    "review_context_notes": {"behavior_score_min": 60},
    "flag_high_priority": {"behavior_score_min": 50},
}


_AUTH_RANK = {
    AuthStrength.BASIC: 0,
    AuthStrength.MFA: 1,
    AuthStrength.STRONG_MFA: 2,
}


def _feature_enabled(feature: str) -> bool:
    return settings.FUNCTIONAL_TRUST_FEATURES.get(feature, False)


def user_has_capability(*, user, capability: str) -> bool:
    if not _feature_enabled("assurance_profile"):
        return True
    requirements = CAPABILITIES.get(capability)
    if not requirements:
        return True
    profile: UserTrustProfile = get_or_create_trust_profile(user=user)
    required_auth = requirements.get("auth_strength")
    if required_auth and _AUTH_RANK.get(profile.auth_strength, 0) < _AUTH_RANK.get(
        required_auth, 0
    ):
        return False
    if requirements.get("identity_verified") and not profile.identity_verified:
        return False
    if requirements.get("role_verified") and not profile.role_verified:
        return False
    behavior_min = requirements.get("behavior_score_min")
    if behavior_min is not None and profile.behavior_score < behavior_min:
        return False
    return True


def require_capability(*, user, capability: str) -> None:
    if not user_has_capability(user=user, capability=capability):
        raise CapabilityError(f"Capability '{capability}' is not available for this account.")
