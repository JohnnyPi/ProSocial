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

    return {
        "shell_unread_notifications": get_unread_notification_count(user=request.user),
        "shell_unread_messages": count_unread_messages(user=request.user),
        "shell_open_actions": list(get_open_actions()[:4]),
        "shell_commitments": list(get_user_commitments(user=request.user)[:3]),
        "shell_pending_invitations": list(
            get_pending_invitations(user=request.user).select_related("inviter__profile")[:3]
        ),
        "shell_user_guilds": list(get_user_guilds(user=request.user)),
    }
