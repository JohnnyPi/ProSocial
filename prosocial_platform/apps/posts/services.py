from django.db import transaction

from apps.common.services import ActivityEventType, record_activity_event
from apps.posts.models import Post


@transaction.atomic
def create_post(*, author, body: str, image=None, image_alt_text: str = "") -> Post:
    post = Post(
        author=author,
        body=body.strip(),
        image_alt_text=image_alt_text.strip(),
    )
    if image and hasattr(image, "read"):
        post.image.save(image.name, image, save=False)
    post.full_clean()
    post.save()
    record_activity_event(
        event_type=ActivityEventType.POST_CREATED,
        actor=author,
        object_type="post",
        object_public_id=post.public_id,
    )
    return post


@transaction.atomic
def update_post(*, post: Post, body: str, image=None, image_alt_text: str = "") -> Post:
    post.body = body.strip()
    post.image_alt_text = image_alt_text.strip()
    if image and hasattr(image, "read"):
        post.image.save(image.name, image, save=False)
    post.full_clean()
    post.save()
    record_activity_event(
        event_type=ActivityEventType.POST_UPDATED,
        actor=post.author,
        object_type="post",
        object_public_id=post.public_id,
    )
    return post


@transaction.atomic
def soft_delete_post(*, post: Post) -> Post:
    post.soft_delete()
    record_activity_event(
        event_type=ActivityEventType.POST_DELETED,
        actor=post.author,
        object_type="post",
        object_public_id=post.public_id,
    )
    return post
