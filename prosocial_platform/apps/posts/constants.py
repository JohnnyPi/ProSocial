from apps.posts.models import PostKind

ACTION_POST_KINDS = frozenset(
    {
        PostKind.HELP_REQUEST,
        PostKind.HELP_OFFER,
        PostKind.ENCOURAGEMENT_REQUEST,
        PostKind.LOCAL_ACTION,
        PostKind.VOLUNTEER_OPPORTUNITY,
    }
)

COMPOSER_KIND_CHOICES = [
    choice for choice in PostKind.choices if choice[0] not in ACTION_POST_KINDS
]

# Short labels for the dashboard feed filter bar.
FEED_KIND_FILTERS: list[tuple[str, str]] = [
    (PostKind.GENERAL, "General"),
    (PostKind.HELP_REQUEST, "Requests"),
    (PostKind.HELP_OFFER, "Offers"),
    (PostKind.ENCOURAGEMENT_REQUEST, "Encouragement"),
    (PostKind.LOCAL_ACTION, "Local actions"),
    (PostKind.VOLUNTEER_OPPORTUNITY, "Volunteers"),
]
