import re

from django.conf import settings
from django.core.exceptions import ValidationError

HANDLE_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


def validate_handle(value: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) < settings.HANDLE_MIN_LENGTH:
        raise ValidationError(
            f"Handle must be at least {settings.HANDLE_MIN_LENGTH} characters."
        )
    if len(normalized) > settings.HANDLE_MAX_LENGTH:
        raise ValidationError(
            f"Handle must be at most {settings.HANDLE_MAX_LENGTH} characters."
        )
    if not HANDLE_PATTERN.match(normalized):
        raise ValidationError("Handle may contain only letters, numbers, and underscores.")
    return normalized
