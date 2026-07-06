"""Domain exceptions for prosocial action state transitions."""


class ProsocialActionError(Exception):
    pass


class InvalidTransitionError(ProsocialActionError):
    pass


ALLOWED_TRANSITIONS = {
    "SAVED": {"COMMITTED", "WITHDRAWN"},
    "COMMITTED": {"COMPLETION_SUBMITTED", "WITHDRAWN"},
    "COMPLETION_SUBMITTED": {"VERIFIED", "REJECTED"},
}


def validate_transition(current: str, target: str) -> None:
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidTransitionError(f"Cannot transition from {current} to {target}.")
