import re

import pytest
from django.urls import reverse

from apps.guilds.services import create_guild


def _nav_link_is_active(content: bytes, href: str) -> bool:
    text = content.decode()
    pattern = rf'<a\s+href="{re.escape(href)}"\s+class="([^"]*)"'
    match = re.search(pattern, text)
    if not match:
        return False
    return "is-active" in match.group(1)


@pytest.mark.django_db
def test_sidebar_home_active_on_dashboard(user, client):
    client.force_login(user)
    response = client.get(reverse("dashboard:index"))
    assert response.status_code == 200
    assert _nav_link_is_active(response.content, reverse("dashboard:index"))
    assert not _nav_link_is_active(response.content, reverse("dashboard:knowledge"))


@pytest.mark.django_db
def test_sidebar_knowledge_active_on_knowledge_hub(user, client):
    client.force_login(user)
    response = client.get(reverse("dashboard:knowledge"))
    assert response.status_code == 200
    assert _nav_link_is_active(response.content, reverse("dashboard:knowledge"))
    assert not _nav_link_is_active(response.content, reverse("dashboard:index"))


@pytest.mark.django_db
def test_sidebar_knowledge_active_on_vault(user, client):
    client.force_login(user)
    response = client.get(reverse("knowledge:vault"))
    assert response.status_code == 200
    assert _nav_link_is_active(response.content, reverse("dashboard:knowledge"))
    assert not _nav_link_is_active(response.content, reverse("dashboard:index"))


@pytest.mark.django_db
def test_knowledge_hub_layout(user, client):
    client.force_login(user)
    response = client.get(reverse("dashboard:knowledge"))
    assert response.status_code == 200
    content = response.content
    assert b"knowledge-hub__hero" in content
    assert b"hub-panel--create" in content
    assert b"Browse all challenges" in content
    assert b"New collection" in content
    assert b"Level" in content
    assert b"Total XP" in content


@pytest.mark.django_db
def test_guild_list_separates_user_and_browse_guilds(user, other_user, client):
    create_guild(creator=user, name="Joined Guild", description="Mine")
    create_guild(creator=other_user, name="Browse Guild", description="Theirs")
    client.force_login(user)
    response = client.get(reverse("guilds:list"))
    assert response.status_code == 200
    content = response.content.decode()
    joined_idx = content.index("Joined Guild")
    browse_idx = content.index("Browse Guild")
    your_idx = content.index("Your guilds")
    browse_section_idx = content.index("Browse guilds")
    assert your_idx < joined_idx < browse_section_idx < browse_idx


@pytest.mark.django_db
def test_actions_list_layout(user, client):
    client.force_login(user)
    response = client.get(reverse("prosocial_actions:action_list"))
    assert response.status_code == 200
    assert b"hub-panel--create" in response.content
    assert b"Open opportunities" in response.content
    assert b"home feed" in response.content


@pytest.mark.django_db
def test_discover_layout(user, client):
    client.force_login(user)
    response = client.get(reverse("discovery:home"))
    assert response.status_code == 200
    assert b"discover-layout" in response.content
    assert b"Recommended for you" in response.content
    assert b"Most clipped" in response.content


@pytest.mark.django_db
def test_messages_layout(user, other_user, client):
    from apps.messaging.services import send_message

    send_message(sender=user, recipient=other_user, body="Hello there")
    client.force_login(user)
    response = client.get(reverse("messaging:list"))
    assert response.status_code == 200
    assert b"hub-panel" in response.content
    assert other_user.profile.public_display_name.encode() in response.content


@pytest.mark.django_db
def test_notifications_layout(user, client):
    client.force_login(user)
    response = client.get(reverse("interactions:notifications"))
    assert response.status_code == 200
    assert b"hub-panel" in response.content
    assert b"Mark all read" in response.content
