from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.models import AccountDeletionRequest
from apps.accounts.services import (
    AccountDeletionError,
    cancel_account_deletion,
    get_pending_deletion_request,
    process_account_deletion,
    process_due_account_deletions,
    request_account_deletion,
)
from apps.common.models import ActivityEvent, ActivityEventType
from apps.interactions.services import create_reply, submit_report
from apps.posts.models import Post, PostKind
from apps.profiles.models import Profile
from apps.prosocial_actions.services import commit_to_action, create_action_post

User = get_user_model()


@pytest.mark.django_db
def test_request_account_deletion_schedules_grace_period(user):
    deletion_request = request_account_deletion(user=user, password="test-pass-123")

    assert deletion_request.is_pending
    assert deletion_request.scheduled_for > timezone.now()
    assert get_pending_deletion_request(user=user) == deletion_request
    assert ActivityEvent.objects.filter(
        actor=user,
        event_type=ActivityEventType.ACCOUNT_DELETION_REQUESTED,
    ).exists()


@pytest.mark.django_db
def test_request_account_deletion_rejects_wrong_password(user):
    with pytest.raises(AccountDeletionError, match="Incorrect password"):
        request_account_deletion(user=user, password="wrong-password")


@pytest.mark.django_db
def test_request_account_deletion_rejects_duplicate_request(user):
    request_account_deletion(user=user, password="test-pass-123")
    with pytest.raises(AccountDeletionError, match="already scheduled"):
        request_account_deletion(user=user, password="test-pass-123")


@pytest.mark.django_db
def test_cancel_account_deletion(user):
    request_account_deletion(user=user, password="test-pass-123")
    cancelled = cancel_account_deletion(user=user)

    assert cancelled.cancelled_at is not None
    assert get_pending_deletion_request(user=user) is None
    assert ActivityEvent.objects.filter(
        actor=user,
        event_type=ActivityEventType.ACCOUNT_DELETION_CANCELLED,
    ).exists()


@pytest.mark.django_db
def test_process_account_deletion_soft_deletes_content_and_removes_user(user, other_user):
    post = Post.objects.create(author=user, body="To be archived")
    reply = create_reply(post=post, author=user, body="My reply")
    report = submit_report(reporter=user, post=post, reason="SPAM", details="test")
    action = create_action_post(
        creator=user,
        kind=PostKind.VOLUNTEER_OPPORTUNITY,
        body="Volunteer",
    )
    commitment = commit_to_action(action=action, participant=other_user)
    user_public_id = user.public_id
    request_account_deletion(user=user, password="test-pass-123")

    process_account_deletion(user=user)

    post.refresh_from_db()
    reply.refresh_from_db()
    report.refresh_from_db()
    action.refresh_from_db()
    commitment.refresh_from_db()

    assert not User.objects.filter(pk=user.pk).exists()
    assert not Profile.objects.filter(user_id=user.pk).exists()
    assert post.deleted_at is not None
    assert post.author_id is None
    assert reply.deleted_at is not None
    assert reply.author_id is None
    assert report.reporter_id is None
    assert action.creator_id is None
    assert commitment.participant_id == other_user.pk
    assert ActivityEvent.objects.filter(
        event_type=ActivityEventType.ACCOUNT_DELETED,
        object_public_id=user_public_id,
        actor__isnull=True,
    ).exists()
    assert AccountDeletionRequest.objects.filter(
        processed_at__isnull=False,
        user__isnull=True,
    ).exists()


@pytest.mark.django_db
def test_process_due_account_deletions(user):
    request_account_deletion(user=user, password="test-pass-123")
    AccountDeletionRequest.objects.filter(user=user).update(
        scheduled_for=timezone.now() - timedelta(minutes=1)
    )

    count = process_due_account_deletions()

    assert count == 1
    assert not User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
def test_account_delete_http_flow(user, client):
    client.force_login(user)
    response = client.post(
        "/accounts/delete/",
        {
            "password": "test-pass-123",
            "confirm": "on",
        },
    )
    assert response.status_code == 302
    assert response.url == "/accounts/login/"
    assert get_pending_deletion_request(user=user) is not None

    client.force_login(user)
    response = client.get("/accounts/delete/")
    assert response.status_code == 200
    assert b"scheduled for permanent deletion" in response.content

    response = client.post("/accounts/delete/cancel/")
    assert response.status_code == 302
    assert get_pending_deletion_request(user=user) is None


@pytest.mark.django_db
def test_account_delete_requires_password_confirmation(user, client):
    client.force_login(user)
    response = client.post(
        "/accounts/delete/",
        {
            "password": "wrong-password",
            "confirm": "on",
        },
    )
    assert response.status_code == 200
    assert get_pending_deletion_request(user=user) is None
