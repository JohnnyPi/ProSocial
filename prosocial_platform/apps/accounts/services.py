from django.db import transaction

from apps.accounts.models import User
from apps.common.services import ActivityEventType, record_activity_event
from apps.profiles.services import create_profile_for_user


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
