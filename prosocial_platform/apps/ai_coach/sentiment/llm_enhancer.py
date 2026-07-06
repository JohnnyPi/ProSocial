import json
import logging
import urllib.request

from django.conf import settings

from apps.ai_coach.sentiment.analyzer import ContentAnalysisResult

logger = logging.getLogger(__name__)


def enhance_with_llm(*, text: str, analysis: ContentAnalysisResult) -> str:
    provider = getattr(settings, "SENTIMENT_LLM_PROVIDER", "") or ""
    api_key = getattr(settings, "SENTIMENT_LLM_API_KEY", "") or ""
    if not provider or not api_key:
        return ""

    timeout = getattr(settings, "SENTIMENT_LLM_TIMEOUT_SECONDS", 5)
    truncated = text[:500]
    payload = {
        "emotion_scores": analysis.emotion_scores,
        "conduct_flags": analysis.conduct_flags,
        "valence": analysis.valence,
        "text_excerpt": truncated,
    }
    prompt = (
        "You are a prosocial writing coach. Given emotion scores and a text excerpt, "
        "offer one brief, non-judgmental coaching sentence about tone or mixed sentiment. "
        "Do not block posting or claim moderation authority. "
        f"Context: {json.dumps(payload)}"
    )

    if provider == "anthropic":
        return _call_anthropic(prompt=prompt, api_key=api_key, timeout=timeout)
    if provider == "openai":
        return _call_openai(prompt=prompt, api_key=api_key, timeout=timeout)
    logger.warning("Unknown SENTIMENT_LLM_PROVIDER: %s", provider)
    return ""


def _call_openai(*, prompt: str, api_key: str, timeout: int) -> str:
    body = json.dumps(
        {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 120,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def _call_anthropic(*, prompt: str, api_key: str, timeout: int) -> str:
    body = json.dumps(
        {
            "model": "claude-3-5-haiku-latest",
            "max_tokens": 120,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["content"][0]["text"].strip()
