from django.db import transaction
from django.utils.text import slugify

from apps.common.models import ActivityEventType
from apps.common.services import record_activity_event
from apps.interactions.models import Reply
from apps.knowledge.models import (
    Clip,
    ClipKind,
    Collection,
    CollectionItem,
    CollectionVisibility,
    PostTag,
    Tag,
)
from apps.posts.models import Post


class KnowledgeError(Exception):
    pass


def _get_or_create_tags(*, slugs: list[str]) -> list[Tag]:
    tags = []
    for slug in slugs:
        normalized = slugify(slug)[:64]
        if not normalized:
            continue
        tag, _ = Tag.objects.get_or_create(
            slug=normalized,
            defaults={"name": slug.replace("-", " ").title()},
        )
        tags.append(tag)
    return tags


@transaction.atomic
def set_post_tags(*, post: Post, tag_slugs: list[str], author=None) -> None:
    if tag_slugs:
        from django.conf import settings

        from apps.trust.services import user_has_privilege

        tag_author = author or post.author
        if (
            settings.FUNCTIONAL_TRUST_FEATURES.get("earned_privileges")
            and tag_author
            and not user_has_privilege(user=tag_author, slug="can_tag_posts")
        ):
            raise KnowledgeError("Tagging requires earned knowledge reputation.")
    PostTag.objects.filter(post=post).delete()
    for tag in _get_or_create_tags(slugs=tag_slugs):
        PostTag.objects.create(post=post, tag=tag)


@transaction.atomic
def create_clip(
    *,
    owner,
    post: Post | None = None,
    reply: Reply | None = None,
    clip_kind: str,
    quoted_text: str = "",
    selection_start: int | None = None,
    selection_end: int | None = None,
    private_note: str = "",
) -> Clip:
    if not post and not reply:
        raise KnowledgeError("Clip must reference a post or reply.")
    if post and reply:
        raise KnowledgeError("Clip cannot reference both post and reply.")
    if clip_kind == ClipKind.WHOLE_THREAD and not post:
        raise KnowledgeError("Whole thread clips require a post.")

    target_post = post or reply.post
    if target_post.deleted_at or target_post.moderation_status != "ACTIVE":
        raise KnowledgeError("Cannot clip removed content.")

    existing = Clip.objects.filter(
        owner=owner,
        post=post,
        reply=reply,
        clip_kind=clip_kind,
        selection_start=selection_start,
        selection_end=selection_end,
    ).first()
    if existing:
        return existing

    clip = Clip.objects.create(
        owner=owner,
        post=post,
        reply=reply,
        clip_kind=clip_kind,
        quoted_text=quoted_text or (reply.body if reply else post.body)[:5000],
        selection_start=selection_start,
        selection_end=selection_end,
        private_note=private_note.strip(),
    )
    record_activity_event(
        event_type=ActivityEventType.CLIP_CREATED,
        actor=owner,
        object_type="clip",
        object_public_id=clip.public_id,
    )
    author = reply.author if reply else post.author
    if author.pk != owner.pk:
        from apps.gamification.models import XPSource
        from apps.gamification.services import award_xp
        from apps.trust.models import TrustEvent, TrustEventType

        award_xp(user=author, source=XPSource.CLIP_BONUS)
        TrustEvent.objects.create(
            user=author,
            event_type=TrustEventType.CLIP_BY_OTHER,
            weight=1.5,
            source_type="clip",
            source_id=str(clip.public_id),
        )
        from apps.trust.services import recalculate_trust_scores

        recalculate_trust_scores(user=author)
    return clip


@transaction.atomic
def create_collection(
    *,
    owner,
    title: str,
    description: str = "",
    visibility: str = CollectionVisibility.PRIVATE,
) -> Collection:
    collection = Collection.objects.create(
        owner=owner,
        title=title.strip(),
        description=description.strip(),
        visibility=visibility,
    )
    record_activity_event(
        event_type=ActivityEventType.COLLECTION_CREATED,
        actor=owner,
        object_type="collection",
        object_public_id=collection.public_id,
    )
    return collection


@transaction.atomic
def add_clip_to_collection(*, collection: Collection, clip: Clip, owner) -> CollectionItem:
    if collection.owner_id != owner.pk or clip.owner_id != owner.pk:
        raise KnowledgeError("You can only add your own clips to your collections.")
    item, created = CollectionItem.objects.get_or_create(
        collection=collection,
        clip=clip,
        defaults={"sort_order": collection.items.count()},
    )
    if not created:
        raise KnowledgeError("Clip already in collection.")
    return item


@transaction.atomic
def add_post_to_collection(*, collection: Collection, post: Post, owner) -> CollectionItem:
    if collection.owner_id != owner.pk:
        raise KnowledgeError("You can only edit your own collections.")
    item, created = CollectionItem.objects.get_or_create(
        collection=collection,
        post=post,
        defaults={"sort_order": collection.items.count()},
    )
    if not created:
        raise KnowledgeError("Post already in collection.")
    return item
