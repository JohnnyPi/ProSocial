from django.core.exceptions import ValidationError

from apps.ai_coach.services import (
    ContentReviewError,
    content_review_required,
    validate_content_review,
)


def enforce_content_review(
    *,
    user,
    text: str,
    review_event_id: int | None,
    surface: str,
) -> None:
    if not content_review_required(text=text):
        return
    try:
        validate_content_review(
            user=user,
            text=text,
            review_event_id=review_event_id,
            surface=surface,
        )
    except ContentReviewError as exc:
        raise ValidationError(str(exc)) from exc


def parse_review_event_id(raw: str | None) -> int | None:
    if not raw:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None
