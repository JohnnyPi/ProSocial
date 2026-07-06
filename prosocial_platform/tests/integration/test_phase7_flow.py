import pytest
from django.contrib.auth import get_user_model

from apps.ai_coach.models import ReflectionJournalEntry, SentimentSnapshot
from apps.ai_coach.services import analyze_sentiment, create_journal_entry, pre_send_prompt, score_content
from apps.posts.models import Post

User = get_user_model()


@pytest.mark.django_db
def test_sentiment_positive():
    label, score = analyze_sentiment(text="Thank you so much for your helpful support!")
    assert label == "POSITIVE"
    assert score > 0


@pytest.mark.django_db
def test_pre_send_prompt_negative():
    prompt = pre_send_prompt(text="You are stupid and I hate this")
    assert prompt is not None


@pytest.mark.django_db
def test_score_content(user):
    post = Post.objects.create(author=user, body="Grateful for this community")
    snapshot = score_content(text=post.body, post=post)
    assert SentimentSnapshot.objects.filter(post=post).exists()
    assert snapshot.label in ("POSITIVE", "NEUTRAL", "NEGATIVE")


@pytest.mark.django_db
def test_journal_entry(user):
    entry = create_journal_entry(user=user, body="Today I helped someone feel heard.")
    assert ReflectionJournalEntry.objects.filter(user=user).exists()
    assert entry.ai_response


@pytest.mark.django_db
def test_pre_send_check_endpoint(user, client):
    client.force_login(user)
    response = client.post(
        "/ai/pre-send-check/",
        {"text": "You are stupid and I hate this"},
    )
    assert response.status_code == 200
    assert b"Reflection prompt" in response.content
