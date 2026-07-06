from django.db import transaction

from apps.common.models import ActivityEventType
from apps.common.services import record_activity_event
from apps.follows.models import PostFollow, UserFollow
from apps.interactions.models import Notification, NotificationKind
from apps.posts.models import Post


class FollowError(Exception):
    pass


@transaction.atomic
def toggle_user_follow(*, follower, following) -> tuple[bool, UserFollow | None]:
    if follower.pk == following.pk:
        raise FollowError("You cannot follow yourself.")
    existing = UserFollow.objects.filter(follower=follower, following=following).first()
    if existing:
        existing.delete()
        return False, None
    follow = UserFollow.objects.create(follower=follower, following=following)
    if follower.pk != following.pk:
        Notification.objects.create(
            recipient=following,
            actor=follower,
            kind=NotificationKind.USER_FOLLOWED,
            payload={"follower_handle": follower.profile.handle},
        )
    record_activity_event(
        event_type=ActivityEventType.USER_FOLLOWED,
        actor=follower,
        metadata={"following_id": following.pk},
    )
    return True, follow


@transaction.atomic
def toggle_post_follow(*, user, post: Post) -> tuple[bool, PostFollow | None]:
    existing = PostFollow.objects.filter(user=user, post=post).first()
    if existing:
        existing.delete()
        return False, None
    follow = PostFollow.objects.create(user=user, post=post)
    if user.pk != post.author_id:
        Notification.objects.create(
            recipient=post.author,
            actor=user,
            kind=NotificationKind.POST_FOLLOWED,
            post=post,
            payload={"post_public_id": str(post.public_id)},
        )
    record_activity_event(
        event_type=ActivityEventType.POST_FOLLOWED,
        actor=user,
        object_type="post",
        object_public_id=post.public_id,
    )
    return True, follow
