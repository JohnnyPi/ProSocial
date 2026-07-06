import pytest
from django.contrib.auth import get_user_model

from apps.follows.models import PostFollow, UserFollow
from apps.follows.services import toggle_post_follow, toggle_user_follow
from apps.knowledge.models import Clip, Collection
from apps.knowledge.services import create_clip, create_collection
from apps.posts.models import Post

User = get_user_model()


@pytest.mark.django_db
def test_clip_post_to_vault(user, other_user):
    post = Post.objects.create(author=other_user, body="Helpful knowledge")
    clip = create_clip(owner=user, post=post, clip_kind="WHOLE_POST")
    assert Clip.objects.filter(owner=user, pk=clip.pk).exists()
    assert clip.quoted_text == "Helpful knowledge"


@pytest.mark.django_db
def test_create_collection(user):
    create_collection(owner=user, title="My notes", description="Saved tips")
    assert Collection.objects.filter(owner=user, title="My notes").exists()


@pytest.mark.django_db
def test_follow_user(user, other_user):
    added, _ = toggle_user_follow(follower=user, following=other_user)
    assert added is True
    assert UserFollow.objects.filter(follower=user, following=other_user).exists()


@pytest.mark.django_db
def test_follow_post(user, other_user):
    post = Post.objects.create(author=other_user, body="Thread to follow")
    added, _ = toggle_post_follow(user=user, post=post)
    assert added is True
    assert PostFollow.objects.filter(user=user, post=post).exists()


@pytest.mark.django_db
def test_knowledge_hub_page(user, client):
    client.force_login(user)
    response = client.get("/dashboard/knowledge/")
    assert response.status_code == 200
    assert b"Knowledge Hub" in response.content
    assert b"knowledge-hub__hero" in response.content


@pytest.mark.django_db
def test_vault_page(user, other_user, client):
    post = Post.objects.create(author=other_user, body="Clip me")
    create_clip(owner=user, post=post, clip_kind="WHOLE_POST")
    client.force_login(user)
    response = client.get("/knowledge/vault/")
    assert response.status_code == 200
    assert b"Clip me" in response.content


@pytest.mark.django_db
def test_create_collection_with_visibility(user):
    from apps.knowledge.models import CollectionVisibility

    collection = create_collection(
        owner=user,
        title="Public notes",
        visibility=CollectionVisibility.PUBLIC,
    )
    assert collection.visibility == CollectionVisibility.PUBLIC


@pytest.mark.django_db
def test_public_collection_readable_by_anonymous(user, client):
    from apps.knowledge.models import CollectionVisibility

    collection = create_collection(
        owner=user,
        title="Open collection",
        visibility=CollectionVisibility.PUBLIC,
    )
    response = client.get(f"/knowledge/collections/{collection.public_id}/")
    assert response.status_code == 200
    assert b"Open collection" in response.content


@pytest.mark.django_db
def test_private_collection_not_readable_by_other(other_user, user, client):
    from apps.knowledge.models import CollectionVisibility

    collection = create_collection(
        owner=user,
        title="Private notes",
        visibility=CollectionVisibility.PRIVATE,
    )
    client.force_login(other_user)
    response = client.get(f"/knowledge/collections/{collection.public_id}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_search_posts_by_body(user, other_user, client):
    Post.objects.create(author=other_user, body="Unique searchable phrase xyz")
    response = client.get("/knowledge/search/", {"q": "searchable phrase"})
    assert response.status_code == 200
    assert b"Unique searchable phrase xyz" in response.content


@pytest.mark.django_db
def test_clip_selection(user, other_user, client):
    post = Post.objects.create(author=other_user, body="Important passage in the post")
    client.force_login(user)
    response = client.post(
        f"/knowledge/clips/post/{post.public_id}/selection/",
        {
            "selection_start": 0,
            "selection_end": 8,
            "quoted_text": "Important",
        },
    )
    assert response.status_code == 302
    assert Clip.objects.filter(owner=user, clip_kind="SELECTION", quoted_text="Important").exists()
