import logging
from dataclasses import dataclass

from django.conf import settings

from apps.ai_coach.models import SentimentLabel
from apps.ai_coach.sentiment.coaching import CoachingResult, build_coaching
from apps.ai_coach.sentiment.conduct import detect_conduct_flags
from apps.ai_coach.sentiment.constants import MODEL_VERSION_LEXICON, MODEL_VERSION_LEXICON_LLM
from apps.ai_coach.sentiment.lexicon import derive_overlays, score_emotions

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ContentAnalysisResult:
    emotion_scores: dict[str, float]
    overlay_scores: dict[str, float]
    conduct_flags: list[str]
    valence: float
    label: str
    score: float
    coaching: CoachingResult
    coaching_summary: str
    model_version: str = MODEL_VERSION_LEXICON
    llm_enhancement: str = ""
    confidence: float = 1.0

    @property
    def all_emotion_scores(self) -> dict[str, float]:
        combined = dict(self.emotion_scores)
        combined.update(self.overlay_scores)
        return combined

    @property
    def top_emotions(self) -> list[tuple[str, float]]:
        return self.coaching.top_emotions


def _derive_label(*, valence: float) -> tuple[str, float]:
    if valence >= 0.25:
        return SentimentLabel.POSITIVE, 0.5 + valence * 0.5
    if valence <= -0.25:
        return SentimentLabel.NEGATIVE, -0.5 + valence * 0.5
    return SentimentLabel.NEUTRAL, valence


def analyze_content(*, text: str, use_llm: bool | None = None) -> ContentAnalysisResult:
    emotion_scores, valence = score_emotions(text=text)
    overlays = derive_overlays(emotion_scores=emotion_scores)
    conduct_flags = detect_conduct_flags(text=text)
    coaching = build_coaching(
        emotion_scores=emotion_scores,
        overlays=overlays,
        conduct_flags=conduct_flags,
        valence=valence,
    )
    label, score = _derive_label(valence=valence)
    summary_parts = [coaching.tone_summary]
    if coaching.coaching_tips:
        summary_parts.append(coaching.coaching_tips[0])
    coaching_summary = " ".join(summary_parts)

    result = ContentAnalysisResult(
        emotion_scores=emotion_scores,
        overlay_scores=overlays,
        conduct_flags=conduct_flags,
        valence=valence,
        label=label,
        score=score,
        coaching=coaching,
        coaching_summary=coaching_summary,
    )

    should_use_llm = use_llm
    if should_use_llm is None:
        should_use_llm = settings.FUNCTIONAL_TRUST_FEATURES.get("sentiment_llm_enhancement", False)

    if should_use_llm:
        from apps.ai_coach.sentiment.llm_enhancer import enhance_with_llm

        try:
            enhancement = enhance_with_llm(text=text, analysis=result)
            if enhancement:
                return ContentAnalysisResult(
                    emotion_scores=result.emotion_scores,
                    overlay_scores=result.overlay_scores,
                    conduct_flags=result.conduct_flags,
                    valence=result.valence,
                    label=result.label,
                    score=result.score,
                    coaching=result.coaching,
                    coaching_summary=f"{coaching_summary} {enhancement}".strip(),
                    model_version=MODEL_VERSION_LEXICON_LLM,
                    llm_enhancement=enhancement,
                    confidence=0.85,
                )
        except Exception:
            logger.exception("LLM sentiment enhancement failed; using lexicon-only result")

    return result
