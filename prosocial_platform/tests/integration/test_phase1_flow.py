import pytest
from django.contrib.auth import get_user_model

from apps.interactions.models import Notification, ProsocialReaction
from apps.interactions.services import (
    block_user,
    create_reply,
    mute_user,
    toggle_prosocial_reaction,
)
from apps.posts.models import Post

User = get_user_model()


@pytest.mark.django_db
def test_create_top_level_reply(user, other_user):
    post = Post.objects.create(author=user, body="Hello")
    reply = create_reply(post=post, author=other_user, body="Nice post")
    assert reply.public_id is not None
    assert Notification.objects.filter(recipient=user, kind="REPLY_RECEIVED").exists()


@pytest.mark.django_db
def test_create_nested_reply(user, other_user):
    post = Post.objects.create(author=user, body="Hello")
    parent = create_reply(post=post, author=other_user, body="Top")
    child = create_reply(post=post, author=user, body="Nested", parent=parent)
    assert child.parent_id == parent.pk


@pytest.mark.django_db
def test_reject_third_nesting_level(user, other_user):
    from apps.interactions.services import InteractionError

    post = Post.objects.create(author=user, body="Hello")
    top = create_reply(post=post, author=other_user, body="Top")
    nested = create_reply(post=post, author=user, body="Nested", parent=top)
    with pytest.raises(InteractionError):
        create_reply(post=post, author=other_user, body="Too deep", parent=nested)


@pytest.mark.django_db
def test_thanks_reaction_on_post(user, other_user):
    post = Post.objects.create(author=user, body="Hello")
    added, _ = toggle_prosocial_reaction(sender=other_user, post=post, kind="THANKS")
    assert added is True
    assert ProsocialReaction.objects.filter(sender=other_user, post=post, kind="THANKS").exists()
    assert Notification.objects.filter(recipient=user, kind="THANK_YOU_RECEIVED").exists()


@pytest.mark.django_db
def test_self_thanks_reaction_rejected(user):
    from apps.interactions.services import InteractionError

    post = Post.objects.create(author=user, body="Hello")
    with pytest.raises(InteractionError):
        toggle_prosocial_reaction(sender=user, post=post, kind="THANKS")


@pytest.mark.django_db
def test_blocked_user_cannot_reply(user, other_user):
    post = Post.objects.create(author=user, body="Hello")
    block_user(blocking_user=user, blocked_user=other_user)
    from apps.interactions.services import BlockedInteractionError

    with pytest.raises(BlockedInteractionError):
        create_reply(post=post, author=other_user, body="Blocked")


@pytest.mark.django_db
def test_muted_user_excluded_from_feed(user, other_user, client):
    Post.objects.create(author=other_user, body="Muted content")
    mute_user(muting_user=user, muted_user=other_user)
    client.force_login(user)
    response = client.get("/dashboard/")
    assert b"Muted content" not in response.content
