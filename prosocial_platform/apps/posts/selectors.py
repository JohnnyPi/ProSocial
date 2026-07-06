import uuid

from django.core.paginator import EmptyPage, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404

from apps.posts.models import Post


def get_dashboard_feed(
    *,
    page: int = 1,
    per_page: int = 20,
    user=None,
    kind: str | None = None,
    feed_mode: str = "all",
):
    queryset = (
        Post.objects.visible()
        .select_related("author", "author__profile", "guild")
        .prefetch_related("post_tags__tag")
        .order_by("-created_at")
    )
    if kind:
        queryset = queryset.filter(kind=kind)
    if user and user.is_authenticated:
        from apps.interactions.selectors import apply_user_boundaries_to_feed

        queryset = apply_user_boundaries_to_feed(queryset=queryset, user=user)
        if feed_mode == "following":
            from apps.follows.selectors import get_following_feed_filter
            from apps.guilds.selectors import get_user_guild_ids

            guild_ids = get_user_guild_ids(user=user)
            follow_filter = get_following_feed_filter(user=user)
            queryset = queryset.filter(follow_filter | Q(guild_id__in=guild_ids))
    paginator = Paginator(queryset, per_page)
    try:
        feed_page = paginator.page(page)
    except EmptyPage:
        feed_page = paginator.page(paginator.num_pages or 1)
    caught_up = feed_mode == "following" and not feed_page.has_next() and paginator.count > 0
    if feed_mode == "caught_up":
        caught_up = True
        feed_page = paginator.page(1)
        if feed_page.has_next():
            caught_up = False
    feed_page.caught_up = caught_up  # type: ignore[attr-defined]
    return feed_page


def get_post_for_display(*, public_id: uuid.UUID) -> Post:
    return get_object_or_404(
        Post.objects.visible()
        .select_related("author", "author__profile")
        .prefetch_related("post_tags__tag"),
        public_id=public_id,
    )


def get_owned_post(*, public_id: uuid.UUID, author) -> Post:
    return get_object_or_404(
        Post.objects.filter(author=author, deleted_at__isnull=True).prefetch_related(
            "post_tags__tag"
        ),
        public_id=public_id,
    )
