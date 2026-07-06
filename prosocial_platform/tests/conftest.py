import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


def review_event_id_for(*, user, text: str, surface: str = "POST") -> int:
    from apps.ai_coach.services import create_content_review_event

    return create_content_review_event(user=user, text=text.strip(), surface=surface).pk


def with_review_event(*, user, data: dict, surface: str = "POST") -> dict:
    body = data.get("body", "")
    if len(body.strip()) >= 8:
        payload = dict(data)
        payload["review_event_id"] = review_event_id_for(user=user, text=body, surface=surface)
        return payload
    return data


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="test-pass-123"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="otheruser", email="other@example.com", password="test-pass-123"
    )
