import pytest
from django.contrib.auth import get_user_model

from apps.profiles.models import Profile

User = get_user_model()


@pytest.mark.django_db
def test_user_has_public_id():
    user = User.objects.create_user(username="alice", email="alice@example.com", password="test-pass-123")
    assert user.public_id is not None


@pytest.mark.django_db
def test_duplicate_email_rejected():
    User.objects.create_user(username="alice", email="alice@example.com", password="test-pass-123")
    with pytest.raises(Exception):
        User.objects.create_user(username="bob", email="alice@example.com", password="test-pass-123")


@pytest.mark.django_db
def test_profile_created_for_new_user():
    user = User.objects.create_user(username="carol", email="carol@example.com", password="test-pass-123")
    assert Profile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_dashboard_creates_missing_profile(client):
    user = User.objects.create_user(username="carol", email="carol@example.com", password="test-pass-123")
    Profile.objects.filter(user=user).delete()
    client.force_login(user)
    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert Profile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_profile_created_on_registration(client):
    response = client.post(
        "/accounts/register/",
        {
            "username": "carol",
            "email": "carol@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "agree_to_terms": True,
        },
    )
    assert response.status_code == 302
    user = User.objects.get(username="carol")
    assert Profile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_handle_case_insensitive_unique():
    user1 = User.objects.create_user(username="dave", email="d1@example.com", password="test-pass-123")
    user2 = User.objects.create_user(username="eve", email="e2@example.com", password="test-pass-123")
    user1.profile.handle = "friendly"
    user1.profile.save()
    user2.profile.handle = "Friendly"
    with pytest.raises(Exception):
        user2.profile.save()
