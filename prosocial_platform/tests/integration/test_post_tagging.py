import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from apps.knowledge.models import PostTag, Tag
from apps.posts.models import Post, PostKind, ThreadType

User = get_user_model()


@pytest.mark.django_db
def test_feed_kind_filters_include_all_post_kinds(user, client):
    client.force_login(user)
    for kind in (
        PostKind.ENCOURAGEMENT_REQUEST,
        PostKind.VOLUNTEER_OPPORTUNITY,
    ):
        Post.objects.create(author=user, body=f"Post for {kind}", kind=kind)

    response = client.get("/dashboard/", {"kind": PostKind.ENCOURAGEMENT_REQUEST})
    assert response.status_code == 200
    assert b"Encouragement" in response.content
    assert b"Post for ENCOURAGEMENT_REQUEST" in response.content
    assert b"Post for VOLUNTEER_OPPORTUNITY" not in response.content


@pytest.mark.django_db
def test_create_post_with_kind_thread_type_and_tags(user, client):
    client.force_login(user)
    response = client.post(
        "/dashboard/",
        {
            "kind": PostKind.HELP_REQUEST,
            "thread_type": ThreadType.KNOWLEDGE_SHARE,
            "title": "Moving tips",
            "body": "Looking for advice on packing boxes.",
            "tags": "moving, neighborhood",
        },
    )
    assert response.status_code == 302

    post = Post.objects.get(author=user, title="Moving tips")
    assert post.kind == PostKind.HELP_REQUEST
    assert post.thread_type == ThreadType.KNOWLEDGE_SHARE
    assert PostTag.objects.filter(post=post).count() == 2
    assert Tag.objects.filter(slug="moving").exists()
    assert Tag.objects.filter(slug="neighborhood").exists()


@pytest.mark.django_db
def test_post_card_shows_tags_and_thread_type(user, other_user, client):
    post = Post.objects.create(
        author=other_user,
        body="Tagged knowledge thread",
        thread_type=ThreadType.KNOWLEDGE_SHARE,
    )
    tag = Tag.objects.create(slug="gardening", name="Gardening")
    PostTag.objects.create(post=post, tag=tag)

    client.force_login(user)
    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert b"Knowledge share" in response.content
    assert b"#Gardening" in response.content
