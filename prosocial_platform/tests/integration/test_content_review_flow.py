import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings

from apps.ai_coach.models import ContentReviewEvent, ContentReviewSurface, SentimentSnapshot
from apps.ai_coach.sentiment.analyzer import analyze_content
from apps.ai_coach.services import (
    ContentReviewError,
    content_review_required,
    create_content_review_event,
)
from apps.interactions.services import create_reply
from apps.posts.models import Post
from apps.posts.services import create_post

User = get_user_model()


@pytest.mark.django_db
def test_analyze_supportive_text():
    result = analyze_content(text="Thank you so much for your helpful and kind support!")
    assert result.label == "POSITIVE"
    assert result.emotion_scores.get("joy", 0) > 0 or result.emotion_scores.get("trust", 0) > 0
    assert "hostile_language" not in result.conduct_flags


@pytest.mark.django_db
def test_analyze_grief_without_conduct_flag():
    result = analyze_content(text="I am grieving and feel deep sadness after this loss.")
    assert "hostile_language" not in result.conduct_flags
    assert result.emotion_scores.get("sadness", 0) > 0 or result.overlay_scores.get("grief", 0) > 0


@pytest.mark.django_db
def test_analyze_hostile_text():
    result = analyze_content(text="You are stupid and I hate you, shut up.")
    assert "hostile_language" in result.conduct_flags
    assert result.coaching.conduct_messages


@pytest.mark.django_db
def test_content_review_endpoint(user, client):
    client.force_login(user)
    response = client.post(
        "/ai/content-review/",
        {"text": "Grateful for this caring community.", "surface": "POST"},
    )
    assert response.status_code == 200
    assert b"data-review-event-id" in response.content
    assert ContentReviewEvent.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_create_post_requires_review(user):
    assert not content_review_required(text="short")
    with pytest.raises(ContentReviewError):
        from apps.ai_coach.services import validate_content_review

        validate_content_review(
            user=user,
            text="This is a long enough post body for review requirement.",
            review_event_id=None,
            surface=ContentReviewSurface.POST,
        )


@pytest.mark.django_db
def test_create_post_with_review_event(user):
    body = "Thank you everyone for the wonderful support in our community."
    event = create_content_review_event(user=user, text=body, surface=ContentReviewSurface.POST)
    post = create_post(author=user, body=body, review_event_id=event.pk)
    assert SentimentSnapshot.objects.filter(post=post).exists()
    snapshot = SentimentSnapshot.objects.get(post=post)
    assert snapshot.emotion_scores
    event.refresh_from_db()
    assert event.is_consumed


@pytest.mark.django_db
def test_create_reply_scores_sentiment(user, other_user):
    post = Post.objects.create(author=other_user, body="Original post")
    body = "Happy to help with a kind and supportive reply here."
    event = create_content_review_event(user=user, text=body, surface=ContentReviewSurface.REPLY)
    reply = create_reply(post=post, author=user, body=body, review_event_id=event.pk)
    assert SentimentSnapshot.objects.filter(reply=reply).exists()


@pytest.mark.django_db
@override_settings(
    FUNCTIONAL_TRUST_FEATURES={
        "content_review": True,
        "sentiment_llm_enhancement": False,
    }
)
def test_post_create_rejects_missing_review(user, client):
    client.force_login(user)
    response = client.post(
        "/dashboard/",
        {
            "body": "This post is long enough to require a content review before publishing.",
            "kind": "GENERAL",
            "thread_type": "DISCUSSION",
        },
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 422
    assert b"review" in response.content.lower()


@pytest.mark.django_db
def test_llm_enhancer_disabled_returns_lexicon_only():
    result = analyze_content(text="Thank you for the help.", use_llm=False)
    assert result.model_version == "nrc-v1"
    assert not result.llm_enhancement
