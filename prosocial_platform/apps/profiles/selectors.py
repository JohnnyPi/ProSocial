from django.shortcuts import get_object_or_404

from apps.profiles.models import Profile


def get_public_profile(*, handle: str) -> Profile:
    return get_object_or_404(Profile.objects.select_related("user"), handle__iexact=handle)
