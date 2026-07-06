import uuid

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.knowledge.models import Clip, Collection, CollectionVisibility, Tag


def get_user_vault(*, user, page: int = 1, per_page: int = 20):
    queryset = (
        Clip.objects.filter(owner=user)
        .select_related("post", "reply", "post__author", "reply__author")
        .order_by("-created_at")
    )
    return Paginator(queryset, per_page).get_page(page)


def get_user_collections(*, user, limit: int | None = None):
    qs = Collection.objects.filter(owner=user).order_by("-updated_at")
    if limit:
        return qs[:limit]
    return qs


def get_collection_for_owner(*, public_id: uuid.UUID, owner) -> Collection:
    return get_object_or_404(
        Collection.objects.prefetch_related("items__clip", "items__post"),
        public_id=public_id,
        owner=owner,
    )


def get_collection_for_display(*, public_id: uuid.UUID, user=None) -> Collection:
    collection = get_object_or_404(
        Collection.objects.prefetch_related(
            "items__clip", "items__post", "owner", "owner__profile"
        ),
        public_id=public_id,
    )
    if collection.owner_id == getattr(user, "pk", None):
        return collection
    if collection.visibility == CollectionVisibility.PUBLIC:
        return collection
    raise Http404


def get_tag_by_slug(*, slug: str) -> Tag:
    return get_object_or_404(Tag, slug=slug)


def get_tagged_posts(*, tag: Tag, page: int = 1, per_page: int = 20):
    from apps.posts.models import Post

    queryset = (
        Post.objects.visible()
        .filter(post_tags__tag=tag)
        .select_related("author", "author__profile")
        .order_by("-created_at")
    )
    return Paginator(queryset, per_page).get_page(page)


def get_popular_tags(*, limit: int = 20):
    return (
        Tag.objects.annotate(post_count=Count("post_tags"))
        .filter(post_count__gt=0)
        .order_by("-post_count")[:limit]
    )


def search_knowledge(*, query: str, page: int = 1, per_page: int = 20):
    from apps.posts.models import Post

    normalized = query.strip()
    if not normalized:
        return Paginator(Post.objects.none(), per_page).get_page(1), []

    posts = (
        Post.objects.visible()
        .filter(Q(body__icontains=normalized) | Q(title__icontains=normalized))
        .select_related("author", "author__profile")
        .order_by("-created_at")
    )
    tags = Tag.objects.filter(Q(name__icontains=normalized) | Q(slug__icontains=normalized))[:10]
    return Paginator(posts, per_page).get_page(page), list(tags)
