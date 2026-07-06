from django.db import transaction
from django.utils import timezone

from apps.common.models import ActivityEventType
from apps.common.services import record_activity_event
from apps.interactions.models import Notification, NotificationKind
from apps.interactions.selectors import is_blocked
from apps.messaging.models import Conversation, Message


class MessagingError(Exception):
    pass


def _ordered_pair(user_a, user_b):
    if user_a.pk < user_b.pk:
        return user_a, user_b
    return user_b, user_a


@transaction.atomic
def get_or_create_conversation(*, user_a, user_b) -> Conversation:
    if is_blocked(user_a=user_a, user_b=user_b):
        raise MessagingError("Messaging is not available.")
    a, b = _ordered_pair(user_a, user_b)
    conversation, _ = Conversation.objects.get_or_create(participant_a=a, participant_b=b)
    return conversation


@transaction.atomic
def send_message(*, sender, recipient, body: str) -> Message:
    body = body.strip()
    if not body:
        raise MessagingError("Message cannot be empty.")
    conversation = get_or_create_conversation(user_a=sender, user_b=recipient)
    message = Message.objects.create(conversation=conversation, sender=sender, body=body)
    if recipient.pk != sender.pk:
        Notification.objects.create(
            recipient=recipient,
            actor=sender,
            kind=NotificationKind.MESSAGE_RECEIVED,
            payload={"conversation_id": str(conversation.public_id)},
        )
    record_activity_event(
        event_type=ActivityEventType.MESSAGE_SENT,
        actor=sender,
        metadata={"recipient_id": recipient.pk},
    )
    return message


@transaction.atomic
def mark_messages_read(*, conversation: Conversation, reader) -> int:
    return Message.objects.filter(
        conversation=conversation,
        read_at__isnull=True,
    ).exclude(sender=reader).update(read_at=timezone.now())
