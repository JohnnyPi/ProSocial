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
def create_profile_for_user(user: User) -> Profile:
    return Profile.objects.create(
        user=user,
        handle=_default_handle(user),
        display_name=user.username,
    )


@transaction.atomic
def update_profile(*, profile: Profile, cleaned_data: dict) -> Profile:
    profile.handle = cleaned_data["handle"]
    profile.display_name = cleaned_data.get("display_name", "")
    profile.biography = cleaned_data.get("biography", "")

    image = cleaned_data.get("profile_image")
    if image and hasattr(image, "read"):
        profile.profile_image.save(image.name, image, save=False)

    profile.save()
    record_activity_event(
        event_type=ActivityEventType.PROFILE_UPDATED,
        actor=profile.user,
        object_type="profile",
        metadata={"handle": profile.handle},
    )
    return profile
