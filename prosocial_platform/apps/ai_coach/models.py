from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class SentimentLabel(models.TextChoices):
    POSITIVE = "POSITIVE", "Positive"
    NEUTRAL = "NEUTRAL", "Neutral"
    NEGATIVE = "NEGATIVE", "Negative"


class SentimentSnapshot(TimeStampedModel):
    post = models.ForeignKey(
        "posts.Post", null=True, blank=True, on_delete=models.CASCADE, related_name="sentiment_snapshots"
    )
    reply = models.ForeignKey(
        "interactions.Reply",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="sentiment_snapshots",
    )
    label = models.CharField(max_length=16, choices=SentimentLabel.choices)
    score = models.FloatField()
    model_version = models.CharField(max_length=32, default="keyword-v1")


class ThreadSummary(TimeStampedModel):
    post = models.OneToOneField("posts.Post", on_delete=models.CASCADE, related_name="ai_summary")
    summary_text = models.TextField(max_length=5000)
    is_ai_generated = models.BooleanField(default=True)


class ReflectionJournalEntry(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journal_entries"
    )
    prompt = models.CharField(max_length=500, blank=True)
    body = models.TextField(max_length=5000)
    ai_response = models.TextField(max_length=2000, blank=True)
    trigger_event = models.CharField(max_length=64, blank=True)


class AIIntervention(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_interventions"
    )
    intervention_type = models.CharField(max_length=64)
    message = models.TextField(max_length=1000)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    post = models.ForeignKey(
        "posts.Post", null=True, blank=True, on_delete=models.SET_NULL, related_name="ai_interventions"
    )
