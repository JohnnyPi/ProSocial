import uuid

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from apps.posts.models import Post


def get_dashboard_feed(*, page: int = 1, per_page: int = 20):
    queryset = (
        Post.objects.visible()
        .select_related("author", "author__profile")
        .order_by("-created_at")
    )
    return Paginator(queryset, per_page).get_page(page)


def get_post_for_display(*, public_id: uuid.UUID) -> Post:
    return get_object_or_404(
        Post.objects.visible().select_related("author", "author__profile"),
        public_id=public_id,
    )


def get_owned_post(*, public_id: uuid.UUID, author) -> Post:
    return get_object_or_404(
        Post.objects.filter(author=author, deleted_at__isnull=True),
        public_id=public_id,
    )
