import pytest
from django.contrib.auth import get_user_model

from apps.discovery.models import RippleLink
from apps.discovery.selectors import get_most_clipped_posts
from apps.knowledge.services import create_clip
from apps.posts.models import Post

User = get_user_model()


@pytest.mark.django_db
def test_most_clipped_posts(user, other_user):
    post = Post.objects.create(author=other_user, body="Wisdom to clip")
    create_clip(owner=user, post=post, clip_kind="WHOLE_POST")
    results = list(get_most_clipped_posts())
    assert any(p.pk == post.pk for p in results)


@pytest.mark.django_db
def test_ripple_link(user, other_user):
    RippleLink.objects.create(
        helper=user, helped=other_user, citation_note="Inspired their approach"
    )
    assert RippleLink.objects.filter(helper=user).exists()


@pytest.mark.django_db
def test_discovery_page(user, client):
    client.force_login(user)
    response = client.get("/discovery/")
    assert response.status_code == 200
