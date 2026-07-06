import re

from django.db import transaction

from apps.ai_coach.models import (
    ReflectionJournalEntry,
    SentimentLabel,
    SentimentSnapshot,
    ThreadSummary,
)
from apps.gamification.models import XPSource
from apps.gamification.services import award_xp

POSITIVE_WORDS = {
    "thank", "thanks", "grateful", "helpful", "support", "kind", "hope", "together",
    "appreciate", "wonderful", "great", "love", "care", "community",
}
NEGATIVE_WORDS = {
    "hate", "stupid", "idiot", "worthless", "kill", "die", "attack", "harass",
    "ugly", "dumb",
}


def analyze_sentiment(*, text: str) -> tuple[str, float]:
    words = set(re.findall(r"[a-z']+", text.lower()))
    pos = len(words & POSITIVE_WORDS)
    neg = len(words & NEGATIVE_WORDS)
    if neg > pos and neg >= 2:
        return SentimentLabel.NEGATIVE, -0.5 - neg * 0.1
    if pos > neg and pos >= 2:
        return SentimentLabel.POSITIVE, 0.5 + pos * 0.1
    return SentimentLabel.NEUTRAL, 0.0


@transaction.atomic
def score_content(*, text: str, post=None, reply=None) -> SentimentSnapshot:
    label, score = analyze_sentiment(text=text)
    return SentimentSnapshot.objects.create(
        post=post,
        reply=reply,
        label=label,
        score=score,
    )


def pre_send_prompt(*, text: str) -> str | None:
    label, score = analyze_sentiment(text=text)
    if label == SentimentLabel.NEGATIVE and score < -0.5:
        return "Before you post — does this say what you mean? Consider whether a calmer phrasing might land better."
    return None


def generate_thread_summary(*, post) -> ThreadSummary:
    replies = post.replies.visible().order_by("created_at")[:10]
    parts = [post.body[:300]]
    for reply in replies:
        parts.append(f"- {reply.body[:150]}")
    summary_text = "Summary:\n" + "\n".join(parts)
    summary, _ = ThreadSummary.objects.update_or_create(
        post=post,
        defaults={"summary_text": summary_text, "is_ai_generated": True},
    )
    return summary


@transaction.atomic
def create_journal_entry(*, user, body: str, prompt: str = "", trigger_event: str = "") -> ReflectionJournalEntry:
    body = body.strip()
    ai_response = "Thank you for taking time to reflect. Your thoughtfulness strengthens the community."
    entry = ReflectionJournalEntry.objects.create(
        user=user,
        body=body,
        prompt=prompt,
        ai_response=ai_response,
        trigger_event=trigger_event,
    )
    award_xp(user=user, source=XPSource.REFLECTION)
    return entry
