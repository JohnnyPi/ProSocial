from apps.posts.models import PostKind

# Short labels for the dashboard feed filter bar.
FEED_KIND_FILTERS: list[tuple[str, str]] = [
    (PostKind.GENERAL, "General"),
    (PostKind.HELP_REQUEST, "Requests"),
    (PostKind.HELP_OFFER, "Offers"),
    (PostKind.ENCOURAGEMENT_REQUEST, "Encouragement"),
    (PostKind.LOCAL_ACTION, "Local actions"),
    (PostKind.VOLUNTEER_OPPORTUNITY, "Volunteers"),
]
