import pytest

from apps.interactions.selectors import get_post_replies
from apps.interactions.services import create_reply, delete_reply
from apps.posts.models import Post


@pytest.mark.django_db
def test_soft_deleted_top_level_reply_excluded(user, other_user):
    post = Post.objects.create(author=user, body="Hello")
    reply = create_reply(post=post, author=other_user, body="Secret reply")
    delete_reply(reply=reply)

    replies = list(get_post_replies(post=post))
    assert replies == []


@pytest.mark.django_db
def test_soft_deleted_nested_reply_excluded_from_children(user, other_user):
    post = Post.objects.create(author=user, body="Hello")
    parent = create_reply(post=post, author=other_user, body="Parent")
    child = create_reply(post=post, author=user, body="Nested secret", parent=parent)
    delete_reply(reply=child)

    replies = list(get_post_replies(post=post))
    assert len(replies) == 1
    assert replies[0].pk == parent.pk
    assert list(replies[0].children.all()) == []


@pytest.mark.django_db
def test_deleted_parent_with_visible_child_retained_for_thread_integrity(user, other_user):
    post = Post.objects.create(author=user, body="Hello")
    parent = create_reply(post=post, author=other_user, body="Parent")
    create_reply(post=post, author=user, body="Still visible", parent=parent)
    delete_reply(reply=parent)

    replies = list(get_post_replies(post=post))
    top_level = [reply for reply in replies if reply.parent_id is None]
    assert len(top_level) == 1
    assert top_level[0].is_deleted
    assert len(list(top_level[0].children.all())) == 1


@pytest.mark.django_db
def test_soft_deleted_reply_not_on_post_detail_page(user, other_user, client):
    post = Post.objects.create(author=user, body="Hello")
    reply = create_reply(post=post, author=other_user, body="Gone forever")
    delete_reply(reply=reply)

    response = client.get(f"/posts/{post.public_id}/")
    assert response.status_code == 200
    assert b"Gone forever" not in response.content
    assert b"Reply removed" not in response.content
