import uuid

from django.db.models import Q
from django.shortcuts import get_object_or_404

from apps.messaging.models import Conversation, Message


def get_user_conversations(*, user):
    return (
        Conversation.objects.filter(Q(participant_a=user) | Q(participant_b=user))
        .select_related(
            "participant_a", "participant_b", "participant_a__profile", "participant_b__profile"
        )
        .order_by("-updated_at")
    )


def get_conversation_for_user(*, public_id: uuid.UUID, user) -> Conversation:
    return get_object_or_404(
        Conversation.objects.filter(Q(participant_a=user) | Q(participant_b=user)),
        public_id=public_id,
    )


def get_conversation_messages(*, conversation: Conversation):
    return conversation.messages.select_related("sender", "sender__profile").order_by("created_at")


def count_unread_messages(*, user) -> int:
    return (
        Message.objects.filter(
            Q(conversation__participant_a=user) | Q(conversation__participant_b=user),
            read_at__isnull=True,
        )
        .exclude(sender=user)
        .count()
    )
