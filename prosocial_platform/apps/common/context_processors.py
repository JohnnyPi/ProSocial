from django.conf import settings
from django.core.cache import cache


def _cached_shell_value(*, user_id: int, key: str, ttl: int, loader):
    cache_key = f"shell:{key}:{user_id}"
    value = cache.get(cache_key)
    if value is None:
        value = loader()
        cache.set(cache_key, value, timeout=ttl)
    return value


def shell_context(request):
    """Sidebar data for the three-column app shell."""
    if not request.user.is_authenticated:
        return {}

    from apps.guilds.selectors import get_user_guilds
    from apps.interactions.selectors import get_unread_notification_count
    from apps.messaging.selectors import count_unread_messages
    from apps.prosocial_actions.selectors import (
        get_open_actions,
        get_pending_invitations,
        get_user_commitments,
    )

    user = request.user
    user_id = user.pk
    ttl = 45

    return {
        "shell_unread_notifications": _cached_shell_value(
            user_id=user_id,
            key="notifications",
            ttl=ttl,
            loader=lambda: get_unread_notification_count(user=user),
        ),
        "shell_unread_messages": _cached_shell_value(
            user_id=user_id,
            key="messages",
            ttl=ttl,
            loader=lambda: count_unread_messages(user=user),
        ),
        "shell_open_actions": _cached_shell_value(
            user_id=user_id,
            key="open_actions",
            ttl=ttl,
            loader=lambda: list(get_open_actions()[:4]),
        ),
        "shell_commitments": _cached_shell_value(
            user_id=user_id,
            key="commitments",
            ttl=ttl,
            loader=lambda: list(get_user_commitments(user=user)[:3]),
        ),
        "shell_pending_invitations": _cached_shell_value(
            user_id=user_id,
            key="invitations",
            ttl=ttl,
            loader=lambda: list(
                get_pending_invitations(user=user).select_related("inviter__profile")[:3]
            ),
        ),
        "shell_user_guilds": _cached_shell_value(
            user_id=user_id,
            key="guilds",
            ttl=ttl,
            loader=lambda: list(get_user_guilds(user=user)),
        ),
    }


def functional_trust_context(request):
    return {"functional_trust_features": settings.FUNCTIONAL_TRUST_FEATURES}
