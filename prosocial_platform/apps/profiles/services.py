from django.db import transaction

from apps.accounts.models import User
from apps.common.services import ActivityEventType, record_activity_event
from apps.profiles.models import Profile


def _default_handle(user: User) -> str:
    base = user.username.lower().replace("-", "_")
    candidate = base[:30]
    suffix = 1
    while Profile.objects.filter(handle__iexact=candidate).exists():
        suffix_str = str(suffix)
        candidate = f"{base[: 30 - len(suffix_str)]}{suffix_str}"
        suffix += 1
    return candidate


@transaction.atomic
def ensure_profile_for_user(user: User) -> Profile:
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            "handle": _default_handle(user),
            "display_name": user.username,
        },
    )
    return profile


create_profile_for_user = ensure_profile_for_user


@transaction.atomic
def update_profile(*, profile: Profile, cleaned_data: dict) -> Profile:
    profile.handle = cleaned_data["handle"]
    profile.display_name = cleaned_data.get("display_name", "")
    profile.biography = cleaned_data.get("biography", "")

    image = cleaned_data.get("profile_image")
    if image and hasattr(image, "read"):
        profile.profile_image.save(image.name, image, save=False)

    header = cleaned_data.get("header_image")
    if header and hasattr(header, "read"):
        profile.header_image.save(header.name, header, save=False)

    profile.save()
    record_activity_event(
        event_type=ActivityEventType.PROFILE_UPDATED,
        actor=profile.user,
        object_type="profile",
        metadata={"handle": profile.handle},
    )
    return profile


@transaction.atomic
def create_endorsement(
    *,
    user,
    claim_type: str,
    claim_label: str,
    verification_method: str,
    issuer: str = "",
    scope: str = "",
):
    from django.conf import settings

    if not settings.FUNCTIONAL_TRUST_FEATURES.get("scoped_endorsements"):
        raise ValueError("Scoped endorsements are not enabled.")
    from apps.profiles.models import EndorsementStatus, ScopedEndorsement, VerificationMethod
    from apps.trust.capabilities import require_capability

    status = EndorsementStatus.PENDING
    if verification_method == VerificationMethod.SELF_ASSERTED:
        status = EndorsementStatus.VERIFIED
    elif verification_method != VerificationMethod.SELF_ASSERTED:
        require_capability(user=user, capability="claim_official_role")
    return ScopedEndorsement.objects.create(
        user=user,
        claim_type=claim_type,
        claim_label=claim_label,
        verification_method=verification_method,
        issuer=issuer,
        scope=scope,
        status=status,
    )


def sync_role_verified_from_endorsement(*, endorsement) -> None:
    from apps.profiles.models import EndorsementStatus, VerificationMethod
    from apps.trust.services import get_or_create_trust_profile

    if endorsement.status != EndorsementStatus.VERIFIED:
        return
    if endorsement.verification_method == VerificationMethod.SELF_ASSERTED:
        return
    profile = get_or_create_trust_profile(user=endorsement.user)
    if not profile.role_verified:
        profile.role_verified = True
        profile.save(update_fields=["role_verified", "updated_at"])
