from apps.profiles.services import ensure_profile_for_user


def ensure_profile_on_user_created(sender, instance, created, **kwargs):
    if created:
        ensure_profile_for_user(instance)
