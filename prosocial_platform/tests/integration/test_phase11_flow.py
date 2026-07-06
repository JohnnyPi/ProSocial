import pytest
from django.contrib.auth import get_user_model

from apps.advanced.models import DonationCampaign, SkillOffering
from apps.advanced.services import create_donation_campaign, record_donation, request_data_export
from apps.ai_coach.services import create_journal_entry
from apps.gamification.services import award_xp
from apps.interactions.services import create_reply
from apps.knowledge.services import create_clip, create_collection
from apps.messaging.services import send_message
from apps.posts.models import Post, PostKind
from apps.prosocial_actions.services import commit_to_action, create_action_post
from apps.trust.services import create_peer_rating

User = get_user_model()

EXPORT_SECTIONS = (
    "export_version",
    "exported_at",
    "account",
    "profile",
    "posts",
    "replies",
    "clips",
    "collections",
    "journal",
    "xp",
    "trust",
    "messages",
    "commitments",
    "follows",
    "boundaries",
    "notifications",
    "donations_and_skills",
    "guild_memberships",
)


@pytest.mark.django_db
def test_donation_campaign_and_record(user):
    campaign = create_donation_campaign(
        creator=user,
        title="Food bank",
        organization_name="Local Food Bank",
    )
    campaign.is_verified = True
    campaign.save()
    donation = record_donation(donor=user, campaign=campaign, amount_cents=1000)
    assert donation.status == "COMPLETED"
    assert donation.amount_cents == 1000


@pytest.mark.django_db
def test_skill_offering(user):
    offering = SkillOffering.objects.create(
        user=user,
        skill_name="Python tutoring",
        description="Help with Django basics",
    )
    assert offering.skill_name == "Python tutoring"


@pytest.mark.django_db
def test_data_export(user):
    export = request_data_export(user=user)
    assert export.status == "COMPLETED"
    assert hasattr(export, "_payload")
    payload = export._payload
    for section in EXPORT_SECTIONS:
        assert section in payload
    assert payload["export_version"] == "1.0"
    assert payload["account"]["email"] == user.email


@pytest.mark.django_db
def test_data_export_includes_user_content(user, other_user):
    post = Post.objects.create(author=user, body="My exported post")
    other_post = Post.objects.create(author=other_user, body="Not mine")
    reply = create_reply(post=post, author=user, body="My reply")
    create_clip(owner=user, post=post, clip_kind="WHOLE_POST")
    create_collection(owner=user, title="Notes", description="Saved ideas")
    create_journal_entry(user=user, body="Reflecting on today")
    award_xp(user=user, source="WELCOME")
    send_message(sender=user, recipient=other_user, body="Private hello")
    action = create_action_post(
        creator=user,
        kind=PostKind.VOLUNTEER_OPPORTUNITY,
        body="Volunteer shift",
    )
    commit_to_action(action=action, participant=other_user)
    create_peer_rating(rater=other_user, post=post, dimension="HELPFUL")

    payload = request_data_export(user=user)._payload

    post_ids = {item["public_id"] for item in payload["posts"]}
    assert str(post.public_id) in post_ids
    assert str(other_post.public_id) not in post_ids

    reply_ids = {item["public_id"] for item in payload["replies"]}
    assert str(reply.public_id) in reply_ids

    assert len(payload["clips"]) == 1
    assert len(payload["collections"]) == 1
    assert len(payload["journal"]) == 1
    assert len(payload["xp"]["transactions"]) >= 1
    assert len(payload["messages"]) == 1
    assert payload["messages"][0]["messages"][0]["body"] == "Private hello"
    assert len(payload["commitments"]["actions_created"]) == 1
    assert payload["trust"]["ratings_received"]
    assert payload["profile"]["handle"] == user.profile.handle


@pytest.mark.django_db
def test_data_export_excludes_other_users_private_messages(user, other_user):
    send_message(sender=other_user, recipient=user, body="Inbound only for user")
    third = User.objects.create_user(
        username="thirduser", email="third@example.com", password="test-pass-123"
    )
    send_message(sender=other_user, recipient=third, body="Not for export user")

    payload = request_data_export(user=user)._payload

    bodies = [
        message["body"]
        for conversation in payload["messages"]
        for message in conversation["messages"]
    ]
    assert "Inbound only for user" in bodies
    assert "Not for export user" not in bodies


@pytest.mark.django_db
def test_data_export_http_download(user, client):
    client.force_login(user)
    response = client.get("/advanced/export/")
    assert response.status_code == 200
    assert response["Content-Disposition"].startswith('attachment; filename="prosocial-export-')
    data = response.json()
    assert data["export_version"] == "1.0"
    assert data["account"]["username"] == user.username


@pytest.mark.django_db
def test_data_export_rate_limited(user, client, settings):
    from django.core.cache import cache

    cache.clear()
    settings.EXPORT_RATE_LIMIT = 1
    client.force_login(user)
    assert client.get("/advanced/export/").status_code == 200
    assert client.get("/advanced/export/").status_code == 429
