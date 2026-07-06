import uuid

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Conversation(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    participant_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_a",
    )
    participant_b = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_b",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["participant_a", "participant_b"],
                name="unique_conversation_pair",
            ),
            models.CheckConstraint(
                condition=~models.Q(participant_a=models.F("participant_b")),
                name="no_self_conversation",
            ),
        ]

    def other_participant(self, user):
        return self.participant_b if self.participant_a_id == user.pk else self.participant_a


class Message(TimeStampedModel):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages_sent"
    )
    body = models.TextField(max_length=2000)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
