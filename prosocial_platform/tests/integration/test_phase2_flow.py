import pytest
from django.contrib.auth import get_user_model

from apps.posts.models import PostKind
from apps.prosocial_actions.models import ActionStatus, CommitmentStatus
from apps.prosocial_actions.services import (
    cancel_action,
    commit_to_action,
    create_action_post,
    save_action,
    submit_completion,
    withdraw_commitment,
)

User = get_user_model()


@pytest.mark.django_db
def test_create_action_post(user):
    action = create_action_post(
        creator=user,
        kind=PostKind.HELP_REQUEST,
        body="Need help moving",
        location_label="Downtown",
    )
    assert action.post.kind == PostKind.HELP_REQUEST
    assert action.status == ActionStatus.OPEN


@pytest.mark.django_db
def test_save_and_commit(user, other_user):
    action = create_action_post(
        creator=user,
        kind=PostKind.HELP_OFFER,
        body="Can help",
    )
    saved = save_action(action=action, participant=other_user)
    assert saved.status == CommitmentStatus.SAVED
    committed = commit_to_action(action=action, participant=other_user)
    assert committed.status == CommitmentStatus.COMMITTED
    assert committed.is_public is False


@pytest.mark.django_db
def test_cannot_commit_after_cancel(user, other_user):
    action = create_action_post(
        creator=user,
        kind=PostKind.LOCAL_ACTION,
        body="Park cleanup",
    )
    cancel_action(action=action, actor=user)
    from apps.prosocial_actions.exceptions import ProsocialActionError

    with pytest.raises(ProsocialActionError):
        commit_to_action(action=action, participant=other_user)


@pytest.mark.django_db
def test_self_reported_completion(user, other_user):
    action = create_action_post(
        creator=user,
        kind=PostKind.VOLUNTEER_OPPORTUNITY,
        body="Volunteer",
    )
    commitment = commit_to_action(action=action, participant=other_user)
    submit_completion(commitment=commitment, participant=other_user, note="Done")
    commitment.refresh_from_db()
    assert commitment.status == CommitmentStatus.VERIFIED


@pytest.mark.django_db
def test_withdraw_commitment(user, other_user):
    action = create_action_post(
        creator=user,
        kind=PostKind.HELP_REQUEST,
        body="Help",
    )
    commitment = commit_to_action(action=action, participant=other_user)
    withdraw_commitment(commitment=commitment, participant=other_user)
    commitment.refresh_from_db()
    assert commitment.status == CommitmentStatus.WITHDRAWN
