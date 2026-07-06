import hashlib
import re
from dataclasses import dataclass

from django.conf import settings
from django.db import transaction

from apps.ai_coach.models import (
    CivilityPromptEvent,
    CivilityPromptType,
    CivilityUserAction,
    ReflectionJournalEntry,
    SentimentLabel,
    SentimentSnapshot,
    ThreadSummary,
)
from apps.gamification.models import XPSource
from apps.gamification.services import award_xp

POSITIVE_WORDS = {
    "thank",
    "thanks",
    "grateful",
    "helpful",
    "support",
    "kind",
    "hope",
    "together",
    "appreciate",
    "wonderful",
    "great",
    "love",
    "care",
    "community",
}
NEGATIVE_WORDS = {
    "hate",
    "stupid",
    "idiot",
    "worthless",
    "kill",
    "die",
    "attack",
    "harass",
    "ugly",
    "dumb",
}
HOSTILE_PATTERNS = [
    r"\b(stupid|idiot|dumb|worthless|hate you)\b",
    r"\b(shut up|go away)\b",
]


@dataclass(frozen=True)
class CivilityResult:
    prompt_type: str
    message: str | None


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def classify_civility(*, text: str) -> CivilityResult:
    if not settings.FUNCTIONAL_TRUST_FEATURES.get("civility_prompts"):
        return CivilityResult(prompt_type=CivilityPromptType.NONE, message=None)
    lower = text.lower()
    label, score = analyze_sentiment(text=text)
    hostile_match = any(re.search(p, lower) for p in HOSTILE_PATTERNS)
    if hostile_match or (label == SentimentLabel.NEGATIVE and score < -0.5):
        return CivilityResult(
            prompt_type=CivilityPromptType.HOSTILE_LANGUAGE,
            message=(
                "This reply may come across as hostile. "
                "Would you like to revise it before posting?"
            ),
        )
    return CivilityResult(prompt_type=CivilityPromptType.NONE, message=None)


def pre_send_prompt(*, text: str) -> str | None:
    result = classify_civility(text=text)
    return result.message


@transaction.atomic
def create_civility_prompt_event(*, user, text: str) -> CivilityPromptEvent | None:
    result = classify_civility(text=text)
    if result.prompt_type == CivilityPromptType.NONE:
        return None
    return CivilityPromptEvent.objects.create(
        user=user,
        prompt_type=result.prompt_type,
        prompt_shown=True,
        original_text_hash=_text_hash(text),
    )


@transaction.atomic
def record_civility_action(
    *,
    event_id: int,
    user,
    user_action: str,
    text: str = "",
) -> CivilityPromptEvent:
    event = CivilityPromptEvent.objects.get(pk=event_id, user=user)
    event.user_action = user_action
    if user_action == CivilityUserAction.EDITED:
        event.edited_after_prompt = True
    if text:
        event.final_text_hash = _text_hash(text)
    event.save(
        update_fields=["user_action", "edited_after_prompt", "final_text_hash", "updated_at"]
    )
    return event


@transaction.atomic
def finalize_civility_event(
    *,
    event_id: int,
    post=None,
    reply=None,
    final_text: str,
) -> CivilityPromptEvent:
    event = CivilityPromptEvent.objects.get(pk=event_id)
    if not event.user_action:
        event.user_action = CivilityUserAction.POSTED_ANYWAY
    if event.original_text_hash != _text_hash(final_text):
        event.edited_after_prompt = True
    event.final_text_hash = _text_hash(final_text)
    event.post = post
    event.reply = reply
    event.is_finalized = True
    event.save(
        update_fields=[
            "user_action",
            "edited_after_prompt",
            "final_text_hash",
            "post",
            "reply",
            "is_finalized",
            "updated_at",
        ]
    )
    return event


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
def create_journal_entry(
    *, user, body: str, prompt: str = "", trigger_event: str = ""
) -> ReflectionJournalEntry:
    body = body.strip()
    ai_response = (
        "Thank you for taking time to reflect. Your thoughtfulness strengthens the community."
    )
    entry = ReflectionJournalEntry.objects.create(
        user=user,
        body=body,
        prompt=prompt,
        ai_response=ai_response,
        trigger_event=trigger_event,
    )
    award_xp(user=user, source=XPSource.REFLECTION)
    return entry
