import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.guilds.models import Guild, GuildMembership
from apps.interactions.models import ContextNote, ContextNoteStatus
from apps.interactions.services import InteractionError, rate_context_note
from apps.trust.clusters import _build_adjacency, get_user_cluster_id, sync_trust_clusters
from apps.trust.models import TrustCluster

User = get_user_model()


@pytest.mark.django_db
def test_build_adjacency_single_guild_query_count(user):
    guild = Guild.objects.create(name="Test Guild", slug="test-guild", created_by=user)
    users = [
        User.objects.create_user(username=f"guser{i}", email=f"guser{i}@example.com", password="x")
        for i in range(5)
    ]
    for user in users:
        GuildMembership.objects.create(user=user, guild=guild)
    with CaptureQueriesContext(connection) as ctx:
        adjacency = _build_adjacency()
    membership_queries = [
        q["sql"] for q in ctx.captured_queries if "guilds_guildmembership" in q["sql"]
    ]
    assert len(membership_queries) == 1
    assert len(adjacency[users[0].pk]) == 4


@pytest.mark.django_db
def test_get_user_cluster_id_no_sync_on_miss(user):
    cluster_id = get_user_cluster_id(user=user)
    assert cluster_id == f"solo_{user.pk}"
    assert TrustCluster.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_sync_trust_clusters_populates_table(user, other_user):
    from apps.follows.models import UserFollow

    UserFollow.objects.create(follower=user, following=other_user)
    count = sync_trust_clusters()
    assert count >= 2
    assert TrustCluster.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_rate_context_note_rejects_non_visible(user, other_user):
    post = __import__("apps.posts.models", fromlist=["Post"]).Post.objects.create(
        author=other_user, body="Post"
    )
    note = ContextNote.objects.create(
        author=other_user,
        post=post,
        body="Pending note",
        status=ContextNoteStatus.PENDING,
    )
    with pytest.raises(InteractionError):
        rate_context_note(rater=user, note=note, is_helpful=True)


@pytest.mark.django_db
def test_rate_context_note_rejects_self_rating(user, other_user):
    post = __import__("apps.posts.models", fromlist=["Post"]).Post.objects.create(
        author=other_user, body="Post"
    )
    note = ContextNote.objects.create(
        author=user,
        post=post,
        body="My note",
        status=ContextNoteStatus.VISIBLE,
    )
    with pytest.raises(InteractionError):
        rate_context_note(rater=user, note=note, is_helpful=True)
