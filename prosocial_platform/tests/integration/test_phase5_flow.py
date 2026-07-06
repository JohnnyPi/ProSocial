import pytest
from django.contrib.auth import get_user_model

from apps.interactions.services import block_user, create_reply, delete_reply
from apps.posts.models import Post
from apps.trust.models import PeerRating, UserTrustProfile
from apps.trust.services import create_peer_rating, recalculate_trust_scores, set_helper_style

User = get_user_model()


@pytest.mark.django_db
def test_helper_style_onboarding(user):
    profile = set_helper_style(user=user, helper_style="SAGE")
    assert profile.helper_style == "SAGE"
    assert profile.helper_style_completed_at is not None


@pytest.mark.django_db
def test_peer_rating_and_trust_recalc(user, other_user):
    post = Post.objects.create(author=other_user, body="Here is help")
    create_peer_rating(rater=user, post=post, dimension="HELPED_ME")
    profile = recalculate_trust_scores(user=other_user)
    assert profile.engagement_trust_score > 0


@pytest.mark.django_db
def test_trust_profile_hidden_by_default(user):
    profile, _ = UserTrustProfile.objects.get_or_create(user=user)
    assert profile.score_visibility == "HIDDEN"


@pytest.mark.django_db
def test_rate_reply(user, other_user):
    post = Post.objects.create(author=other_user, body="Question")
    reply = create_reply(post=post, author=other_user, body="Answer")
    create_peer_rating(rater=user, reply=reply, dimension="HELPFUL")
    assert reply.peer_ratings.filter(rater=user).exists()


@pytest.mark.django_db
def test_rate_deleted_reply_returns_404(user, other_user, client):
    post = Post.objects.create(author=other_user, body="Question")
    reply = create_reply(post=post, author=other_user, body="Answer")
    delete_reply(reply=reply)
    client.force_login(user)

    response = client.post(
        f"/trust/rate/reply/{reply.public_id}/",
        {"dimension": "HELPFUL"},
    )
    assert response.status_code == 404
    assert not PeerRating.objects.filter(rater=user, reply=reply).exists()


@pytest.mark.django_db
def test_rate_reply_blocked_user_returns_403(user, other_user, client):
    post = Post.objects.create(author=other_user, body="Question")
    reply = create_reply(post=post, author=other_user, body="Answer")
    block_user(blocking_user=other_user, blocked_user=user)
    client.force_login(user)

    response = client.post(
        f"/trust/rate/reply/{reply.public_id}/",
        {"dimension": "HELPFUL"},
    )
    assert response.status_code == 403
    assert not PeerRating.objects.filter(rater=user, reply=reply).exists()


@pytest.mark.django_db
def test_rate_post_blocked_user_returns_403(user, other_user, client):
    post = Post.objects.create(author=other_user, body="Question")
    block_user(blocking_user=other_user, blocked_user=user)
    client.force_login(user)

    response = client.post(
        f"/trust/rate/post/{post.public_id}/",
        {"dimension": "HELPFUL"},
    )
    assert response.status_code == 403
    assert not PeerRating.objects.filter(rater=user, post=post).exists()


@pytest.mark.django_db
def test_clip_by_other_recalculates_trust(user, other_user):
    post = Post.objects.create(author=other_user, body="Wisdom")
    from apps.knowledge.services import create_clip
    from apps.trust.services import get_or_create_trust_profile

    create_clip(owner=user, post=post, clip_kind="WHOLE_POST")
    profile = get_or_create_trust_profile(user=other_user)
    assert profile.engagement_trust_score > 40.0
