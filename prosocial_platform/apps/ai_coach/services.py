import hashlib
from dataclasses import dataclass

from django.conf import settings
from django.db import transaction

from apps.ai_coach.models import (
    AIIntervention,
    CivilityPromptEvent,
    CivilityPromptType,
    CivilityUserAction,
    ContentReviewEvent,
    ReflectionJournalEntry,
    SentimentSnapshot,
    ThreadSummary,
)
from apps.ai_coach.sentiment.analyzer import ContentAnalysisResult, analyze_content
from apps.ai_coach.sentiment.conduct import detect_conduct_flags
from apps.ai_coach.sentiment.constants import CONTENT_REVIEW_MIN_LENGTH
from apps.gamification.models import XPSource
from apps.gamification.services import award_xp

CIVILITY_CONDUCT_FLAGS = {"hostile_language", "dehumanization", "threat"}


class ContentReviewError(Exception):
    pass


@dataclass(frozen=True)
class CivilityResult:
    prompt_type: str
    message: str | None


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_review_required(*, text: str) -> bool:
    if not settings.FUNCTIONAL_TRUST_FEATURES.get("content_review"):
        return False
    return len(text.strip()) >= CONTENT_REVIEW_MIN_LENGTH


def analyze_sentiment(*, text: str) -> tuple[str, float]:
    result = analyze_content(text=text)
    return result.label, result.score


@transaction.atomic
def score_content(
    *,
    text: str,
    post=None,
    reply=None,
    analysis: ContentAnalysisResult | None = None,
) -> SentimentSnapshot:
    if analysis is None:
        analysis = analyze_content(text=text)
    return SentimentSnapshot.objects.create(
        post=post,
        reply=reply,
        label=analysis.label,
        score=analysis.score,
        emotion_scores=analysis.all_emotion_scores,
        conduct_flags=analysis.conduct_flags,
        coaching_summary=analysis.coaching_summary,
        confidence=analysis.confidence,
        model_version=analysis.model_version,
    )


@transaction.atomic
def create_content_review_event(
    *,
    user,
    text: str,
    surface: str,
) -> ContentReviewEvent:
    text = text.strip()
    if len(text) < CONTENT_REVIEW_MIN_LENGTH:
        raise ContentReviewError("Text is too short to review.")
    analysis = analyze_content(text=text)
    return ContentReviewEvent.objects.create(
        user=user,
        surface=surface,
        text_hash=_text_hash(text),
        emotion_scores=analysis.all_emotion_scores,
        conduct_flags=analysis.conduct_flags,
        coaching_summary=analysis.coaching_summary,
        coaching_tips=analysis.coaching.coaching_tips,
        tone_summary=analysis.coaching.tone_summary,
        label=analysis.label,
        score=analysis.score,
        model_version=analysis.model_version,
    )


def get_content_review_event(*, event_id: int, user) -> ContentReviewEvent:
    return ContentReviewEvent.objects.get(pk=event_id, user=user)


def validate_content_review(
    *,
    user,
    text: str,
    review_event_id: int | None,
    surface: str,
) -> ContentReviewEvent:
    if not content_review_required(text=text):
        raise ContentReviewError("Review not required for this content.")
    if not review_event_id:
        raise ContentReviewError("Please review your content before publishing.")
    try:
        event = get_content_review_event(event_id=review_event_id, user=user)
    except ContentReviewEvent.DoesNotExist as exc:
        raise ContentReviewError("Please review your content before publishing.") from exc
    if event.is_consumed:
        raise ContentReviewError("This review has already been used. Please review again.")
    if event.surface != surface:
        raise ContentReviewError("Review does not match this form. Please review again.")
    text = text.strip()
    if event.text_hash != _text_hash(text):
        raise ContentReviewError("Content changed after review. Please review again.")
    return event


@transaction.atomic
def score_from_review_event(
    *, event: ContentReviewEvent, post=None, reply=None
) -> SentimentSnapshot:
    return SentimentSnapshot.objects.create(
        post=post,
        reply=reply,
        label=event.label,
        score=event.score,
        emotion_scores=event.emotion_scores,
        conduct_flags=event.conduct_flags,
        coaching_summary=event.coaching_summary,
        model_version=event.model_version,
    )


@transaction.atomic
def finalize_content_review_event(
    *,
    event_id: int,
    post=None,
    reply=None,
    final_text: str,
) -> ContentReviewEvent:
    event = ContentReviewEvent.objects.select_for_update().get(pk=event_id)
    final_hash = _text_hash(final_text.strip())
    if event.text_hash != final_hash:
        event.edited_after_review = True
    event.post = post
    event.reply = reply
    event.is_finalized = True
    event.is_consumed = True
    event.save(
        update_fields=[
            "edited_after_review",
            "post",
            "reply",
            "is_finalized",
            "is_consumed",
            "updated_at",
        ]
    )
    return event


def classify_civility(*, text: str) -> CivilityResult:
    if not settings.FUNCTIONAL_TRUST_FEATURES.get("civility_prompts"):
        return CivilityResult(prompt_type=CivilityPromptType.NONE, message=None)
    conduct_flags = detect_conduct_flags(text=text)
    if conduct_flags:
        return CivilityResult(
            prompt_type=CivilityPromptType.HOSTILE_LANGUAGE,
            message=(
                "This reply may come across as hostile. "
                "Would you like to revise it before posting?"
            ),
        )
    return CivilityResult(prompt_type=CivilityPromptType.NONE, message=None)


def civility_prompt_needed(*, conduct_flags: list[str]) -> bool:
    return bool(set(conduct_flags) & CIVILITY_CONDUCT_FLAGS)


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
    if user_action == CivilityUserAction.POSTED_ANYWAY:
        AIIntervention.objects.create(
            user=user,
            intervention_type="HOSTILE_POSTED_ANYWAY",
            message=(
                "You chose to post content flagged for conduct concerns. "
                "Consider revisiting community guidelines if this becomes a pattern."
            ),
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
    if event.user_action == CivilityUserAction.POSTED_ANYWAY:
        pending = (
            AIIntervention.objects.filter(
                user=event.user,
                intervention_type="HOSTILE_POSTED_ANYWAY",
                post__isnull=True,
                dismissed_at__isnull=True,
            )
            .order_by("-created_at")
            .first()
        )
        if pending:
            pending.post = post
            pending.save(update_fields=["post", "updated_at"])
    return event


def get_undismissed_interventions(*, user):
    return AIIntervention.objects.filter(user=user, dismissed_at__isnull=True).order_by(
        "-created_at"
    )


@transaction.atomic
def dismiss_intervention(*, intervention_id: int, user) -> AIIntervention:
    intervention = AIIntervention.objects.get(pk=intervention_id, user=user)
    from django.utils import timezone

    intervention.dismissed_at = timezone.now()
    intervention.save(update_fields=["dismissed_at", "updated_at"])
    return intervention


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
