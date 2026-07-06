import logging
import uuid
from typing import Any

from apps.common.models import ActivityEvent

logger = logging.getLogger(__name__)


def record_activity_event(
    *,
    event_type: str,
    actor=None,
    object_type: str = "",
    object_public_id: uuid.UUID | None = None,
    metadata: dict[str, Any] | None = None,
    request_id: str = "",
) -> None:
    """Record an activity event without breaking the caller on failure."""
    try:
        ActivityEvent.objects.create(
            actor=actor,
            event_type=event_type,
            object_type=object_type,
            object_public_id=object_public_id,
            metadata=metadata or {},
            request_id=request_id,
        )
    except Exception:
        logger.exception("Failed to record activity event: %s", event_type)
