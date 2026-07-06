from dataclasses import dataclass

from apps.ai_coach.sentiment.constants import (
    CONDUCT_LABELS,
    EMOTION_LABELS,
    OVERLAY_EMOTIONS,
)


@dataclass(frozen=True)
class CoachingResult:
    tone_summary: str
    top_emotions: list[tuple[str, float]]
    coaching_tips: list[str]
    conduct_messages: list[str]


def _top_emotions(
    emotion_scores: dict[str, float],
    overlays: dict[str, float],
    *,
    limit: int = 5,
) -> list[tuple[str, float]]:
    combined = dict(emotion_scores)
    for name in OVERLAY_EMOTIONS:
        if name in overlays and overlays[name] > 0.15:
            combined[name] = overlays[name]
    ranked = sorted(combined.items(), key=lambda item: item[1], reverse=True)
    return [(k, v) for k, v in ranked if v >= 0.15][:limit]


def build_coaching(
    *,
    emotion_scores: dict[str, float],
    overlays: dict[str, float],
    conduct_flags: list[str],
    valence: float,
) -> CoachingResult:
    top = _top_emotions(emotion_scores, overlays)
    tips: list[str] = []
    conduct_messages = [CONDUCT_LABELS[f] for f in conduct_flags if f in CONDUCT_LABELS]

    if conduct_flags:
        tone = "Your message may be read as confrontational."
        tips.append("Consider focusing on the issue rather than the person.")
        tips.append("Try naming what you hope will change instead of what frustrates you.")
    elif overlays.get("grief", 0) >= 0.4:
        tone = "You're sharing something difficult — that kind of honesty is welcome here."
        tips.append("It's okay to ask for support directly if that would help.")
    elif overlays.get("emotional_support", 0) >= 0.4:
        tone = "Warm and supportive — this reads as care for others."
        tips.append("Specific examples of what helped can make support even more useful.")
    elif overlays.get("constructive_criticism", 0) >= 0.35:
        tone = "Critical but engaged — you're raising concerns while staying in conversation."
        tips.append("Lead with shared goals before the critique to keep dialogue open.")
    elif overlays.get("frustration", 0) >= 0.4 and not conduct_flags:
        tone = "Frustration comes through — strong feelings are allowed; personal attacks are not."
        tips.append("Describe the impact on you or the community rather than labeling others.")
    elif valence >= 0.35:
        tone = "Overall tone reads as positive and constructive."
    elif valence <= -0.35:
        tone = "Overall tone reads as strongly negative — check that matches your intent."
        tips.append(
            "Negative emotions are fine; consider whether anything might read as a personal attack."
        )
    else:
        tone = "Balanced or mixed tone — neither strongly positive nor negative."

    if not tips and top:
        primary = top[0][0]
        label = EMOTION_LABELS.get(primary, primary.replace("_", " ").title())
        tips.append(f"Primary signal: {label}. Make sure that matches what you want to convey.")

    if not tips:
        tips.append("Read once more before posting to ensure your message says what you mean.")

    return CoachingResult(
        tone_summary=tone,
        top_emotions=top,
        coaching_tips=tips[:2],
        conduct_messages=conduct_messages,
    )
