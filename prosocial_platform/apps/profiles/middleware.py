from apps.profiles.services import ensure_profile_for_user


def ensure_user_profile(get_response):
    def middleware(request):
        if request.user.is_authenticated and not hasattr(request.user, "profile"):
            ensure_profile_for_user(request.user)
        return get_response(request)

    return middleware
