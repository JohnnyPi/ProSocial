from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import AccountDeletionRequest, User
from apps.common.models import ActivityEvent
from apps.common.services import ActivityEventType, record_activity_event
from apps.profiles.services import create_profile_for_user


class AccountDeletionError(Exception):
    pass


@transaction.atomic
def register_user(*, username: str, email: str, password: str) -> User:
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    create_profile_for_user(user)
    record_activity_event(
        event_type=ActivityEventType.ACCOUNT_REGISTERED,
        actor=user,
        object_type="user",
        object_public_id=user.public_id,
        metadata={"username": user.username},
    )
    return user


def get_pending_deletion_request(*, user) -> AccountDeletionRequest | None:
    return (
        AccountDeletionRequest.objects.filter(
            user=user,
            cancelled_at__isnull=True,
            processed_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )


@transaction.atomic
def request_account_deletion(*, user, password: str) -> AccountDeletionRequest:
    if not user.check_password(password):
        raise AccountDeletionError("Incorrect password.")
    if get_pending_deletion_request(user=user):
        raise AccountDeletionError("Account deletion is already scheduled.")

    scheduled_for = timezone.now() + timedelta(days=settings.ACCOUNT_DELETION_GRACE_DAYS)
    deletion_request = AccountDeletionRequest.objects.create(
        user=user,
        scheduled_for=scheduled_for,
    )
    record_activity_event(
        event_type=ActivityEventType.ACCOUNT_DELETION_REQUESTED,
        actor=user,
        object_type="user",
        object_public_id=user.public_id,
        metadata={"scheduled_for": scheduled_for.isoformat()},
    )
    return deletion_request


@transaction.atomic
def cancel_account_deletion(*, user) -> AccountDeletionRequest:
    deletion_request = get_pending_deletion_request(user=user)
    if deletion_request is None:
        raise AccountDeletionError("No pending account deletion request was found.")

    deletion_request.cancelled_at = timezone.now()
    deletion_request.save(update_fields=["cancelled_at", "updated_at"])
    record_activity_event(
        event_type=ActivityEventType.ACCOUNT_DELETION_CANCELLED,
        actor=user,
        object_type="user",
        object_public_id=user.public_id,
    )
    return deletion_request


@transaction.atomic
def process_account_deletion(*, user) -> None:
    from apps.interactions.models import Reply
    from apps.posts.models import Post

    user_public_id = str(user.public_id)
    now = timezone.now()

    Post.objects.filter(author=user, deleted_at__isnull=True).update(deleted_at=now)
    Reply.objects.filter(author=user, deleted_at__isnull=True).update(deleted_at=now)

    record_activity_event(
        event_type=ActivityEventType.ACCOUNT_DELETED,
        actor=None,
        object_type="user",
        object_public_id=user.public_id,
        metadata={"username": user.username},
    )
    ActivityEvent.objects.filter(actor=user).update(actor=None)

    AccountDeletionRequest.objects.filter(user=user, processed_at__isnull=True).update(
        processed_at=now
    )
    user.delete()


def process_due_account_deletions() -> int:
    due_requests = (
        AccountDeletionRequest.objects.filter(
            scheduled_for__lte=timezone.now(),
            cancelled_at__isnull=True,
            processed_at__isnull=True,
        )
        .select_related("user")
        .order_by("scheduled_for")
    )
    count = 0
    for deletion_request in due_requests:
        process_account_deletion(user=deletion_request.user)
        count += 1
    return count
