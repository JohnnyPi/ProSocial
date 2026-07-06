from django.db.models import Q

from apps.follows.models import PostFollow, UserFollow


def is_following_user(*, follower, following) -> bool:
    return UserFollow.objects.filter(follower=follower, following=following).exists()


def is_following_post(*, user, post) -> bool:
    return PostFollow.objects.filter(user=user, post=post).exists()


def get_followed_user_ids(*, user) -> list[int]:
    return list(UserFollow.objects.filter(follower=user).values_list("following_id", flat=True))


def get_followed_post_ids(*, user) -> list[int]:
    return list(PostFollow.objects.filter(user=user).values_list("post_id", flat=True))


def get_following_feed_filter(*, user):
    followed_users = get_followed_user_ids(user=user)
    followed_posts = get_followed_post_ids(user=user)
    return Q(author_id__in=followed_users) | Q(pk__in=followed_posts)
