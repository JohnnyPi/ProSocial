import pytest
from django.contrib.auth import get_user_model

from apps.guilds.models import GuildMembership
from apps.guilds.services import create_guild, join_guild
from apps.interactions.models import ProsocialReaction
from apps.messaging.services import send_message
from apps.posts.models import Post

User = get_user_model()


@pytest.mark.django_db
def test_create_and_join_guild(user, other_user):
    guild = create_guild(creator=user, name="Local Helpers", description="Neighborhood aid")
    assert GuildMembership.objects.filter(guild=guild, user=user, role="LEADER").exists()
    join_guild(user=other_user, guild=guild)
    assert GuildMembership.objects.filter(guild=guild, user=other_user).exists()


@pytest.mark.django_db
def test_guild_post_feed(user):
    guild = create_guild(creator=user, name="Test Guild")
    Post.objects.create(author=user, body="Guild post", guild=guild)
    from apps.guilds.selectors import get_guild_feed

    page = get_guild_feed(guild=guild)
    assert page.object_list.count() == 1


@pytest.mark.django_db
def test_send_message(user, other_user):
    msg = send_message(sender=user, recipient=other_user, body="Hello there")
    assert msg.body == "Hello there"


@pytest.mark.django_db
def test_following_feed(user, other_user, client):
    Post.objects.create(author=other_user, body="Followed content")
    from apps.follows.services import toggle_user_follow

    toggle_user_follow(follower=user, following=other_user)
    client.force_login(user)
    response = client.get("/dashboard/?feed=following")
    assert response.status_code == 200
    assert b"Followed content" in response.content


@pytest.mark.django_db
def test_prosocial_reaction(user, other_user):
    post = Post.objects.create(author=other_user, body="Great idea")
    ProsocialReaction.objects.create(sender=user, post=post, kind="SUPPORTIVE")
    assert ProsocialReaction.objects.filter(sender=user, post=post).exists()
