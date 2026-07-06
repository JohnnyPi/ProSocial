from django.db import transaction

from apps.common.services import ActivityEventType, record_activity_event
from apps.posts.constants import ACTION_POST_KINDS
from apps.posts.exceptions import PostError
from apps.posts.models import Post, PostKind, ThreadType


@transaction.atomic
def create_post(
    *,
    author,
    body: str,
    image=None,
    image_alt_text: str = "",
    kind: str = PostKind.GENERAL,
    thread_type: str = ThreadType.DISCUSSION,
    title: str = "",
    tag_slugs: list[str] | None = None,
    civility_event_id: int | None = None,
    review_event_id: int | None = None,
    _allow_action_kind: bool = False,
) -> Post:
    if kind in ACTION_POST_KINDS and not _allow_action_kind:
        raise PostError(
            "Use the Actions module to create help requests, offers, and volunteer posts."
        )
    post = Post(
        author=author,
        body=body.strip(),
        image_alt_text=image_alt_text.strip(),
        kind=kind,
        thread_type=thread_type,
        title=title.strip(),
    )
    if image and hasattr(image, "read"):
        post.image.save(image.name, image, save=False)
    post.full_clean()
    post.save()
    if tag_slugs:
        from apps.knowledge.services import set_post_tags

        set_post_tags(post=post, tag_slugs=tag_slugs, author=author)
    from apps.moderation.services import flag_crisis_content

    flag_crisis_content(text=post.body, post=post)
    if civility_event_id:
        from apps.ai_coach.services import finalize_civility_event

        finalize_civility_event(event_id=civility_event_id, post=post, final_text=post.body)
    if review_event_id:
        from apps.ai_coach.services import finalize_content_review_event, score_from_review_event

        event = finalize_content_review_event(
            event_id=review_event_id, post=post, final_text=post.body
        )
        score_from_review_event(event=event, post=post)
    else:
        from apps.ai_coach.services import score_content

        score_content(text=post.body, post=post)
    record_activity_event(
        event_type=ActivityEventType.POST_CREATED,
        actor=author,
        object_type="post",
        object_public_id=post.public_id,
    )
    return post


@transaction.atomic
def update_post(
    *,
    post: Post,
    body: str,
    image=None,
    image_alt_text: str = "",
    kind: str | None = None,
    thread_type: str | None = None,
    title: str | None = None,
    tag_slugs: list[str] | None = None,
    civility_event_id: int | None = None,
    review_event_id: int | None = None,
) -> Post:
    if kind is not None and kind in ACTION_POST_KINDS:
        raise PostError("Use the Actions module to set action post kinds.")
    post.body = body.strip()
    post.image_alt_text = image_alt_text.strip()
    if kind is not None:
        post.kind = kind
    if thread_type is not None:
        post.thread_type = thread_type
    if title is not None:
        post.title = title.strip()
    if image and hasattr(image, "read"):
        post.image.save(image.name, image, save=False)
    post.full_clean()
    post.save()
    if tag_slugs is not None:
        from apps.knowledge.services import set_post_tags

        set_post_tags(post=post, tag_slugs=tag_slugs, author=post.author)
    from apps.moderation.services import flag_crisis_content

    flag_crisis_content(text=post.body, post=post)
    if civility_event_id:
        from apps.ai_coach.services import finalize_civility_event

        finalize_civility_event(event_id=civility_event_id, post=post, final_text=post.body)
    if review_event_id:
        from apps.ai_coach.services import finalize_content_review_event, score_from_review_event

        event = finalize_content_review_event(
            event_id=review_event_id, post=post, final_text=post.body
        )
        score_from_review_event(event=event, post=post)
    record_activity_event(
        event_type=ActivityEventType.POST_UPDATED,
        actor=post.author,
        object_type="post",
        object_public_id=post.public_id,
    )
    return post


@transaction.atomic
def soft_delete_post(*, post: Post, record_event: bool = True) -> Post:
    post.soft_delete()
    if record_event and post.author_id:
        record_activity_event(
            event_type=ActivityEventType.POST_DELETED,
            actor=post.author,
            object_type="post",
            object_public_id=post.public_id,
        )
    return post
