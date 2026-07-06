import json
import re
from functools import lru_cache
from pathlib import Path

from apps.ai_coach.sentiment.constants import NRC_EMOTIONS

_LEXICON_PATH = Path(__file__).resolve().parent.parent / "data" / "nrc_lexicon.json"

_BUILTIN_LEXICON: dict[str, dict[str, float]] = {}


def _add_words(emotion: str, words: set[str]) -> None:
    for word in words:
        entry = _BUILTIN_LEXICON.setdefault(word, {})
        entry[emotion] = entry.get(emotion, 0.0) + 1.0


_add_words(
    "joy",
    {
        "happy",
        "happiness",
        "joy",
        "joyful",
        "delight",
        "delighted",
        "glad",
        "cheerful",
        "celebrate",
        "celebration",
        "wonderful",
        "great",
        "awesome",
        "fantastic",
        "love",
        "lovely",
        "beautiful",
        "smile",
        "laugh",
        "laughter",
        "fun",
        "funny",
        "excited",
        "excitement",
        "thrilled",
        "grateful",
        "gratitude",
        "thank",
        "thanks",
        "thankful",
        "blessed",
        "hope",
        "hopeful",
        "optimistic",
        "bright",
        "sunny",
        "win",
        "victory",
        "success",
        "successful",
        "proud",
        "pride",
        "pleased",
        "pleasure",
        "enjoy",
        "enjoying",
        "bliss",
        "ecstatic",
        "elated",
        "jubilant",
        "merry",
        "playful",
        "amazing",
        "brilliant",
        "excellent",
        "perfect",
        "sweet",
        "warm",
        "heartwarming",
    },
)
_add_words(
    "trust",
    {
        "trust",
        "trusted",
        "trustworthy",
        "faith",
        "faithful",
        "honest",
        "honesty",
        "reliable",
        "dependable",
        "loyal",
        "loyalty",
        "support",
        "supportive",
        "help",
        "helpful",
        "helping",
        "care",
        "caring",
        "kind",
        "kindness",
        "compassion",
        "compassionate",
        "empathy",
        "empathetic",
        "understand",
        "understanding",
        "listen",
        "listening",
        "respect",
        "respectful",
        "community",
        "together",
        "collaborate",
        "cooperate",
        "safe",
        "safety",
        "secure",
        "believe",
        "confident",
        "confidence",
        "reassure",
        "reassuring",
        "appreciate",
        "appreciation",
        "solidarity",
        "ally",
        "friend",
        "friendship",
        "neighbor",
        "neighbors",
        "volunteer",
        "mentor",
    },
)
_add_words(
    "sadness",
    {
        "sad",
        "sadness",
        "unhappy",
        "depressed",
        "depression",
        "grief",
        "grieving",
        "mourn",
        "mourning",
        "loss",
        "lost",
        "lonely",
        "loneliness",
        "alone",
        "hurt",
        "hurting",
        "pain",
        "painful",
        "ache",
        "aching",
        "cry",
        "crying",
        "tears",
        "heartbroken",
        "heartbreak",
        "miss",
        "missing",
        "regret",
        "sorry",
        "sorrow",
        "melancholy",
        "blue",
        "down",
        "hopeless",
        "despair",
        "empty",
        "abandoned",
        "abandonment",
        "bereaved",
        "devastated",
        "devastating",
        "tragic",
        "tragedy",
        "unfair",
        "struggling",
        "struggle",
        "hardship",
        "difficult",
        "hard",
        "tough",
    },
)
_add_words(
    "anger",
    {
        "angry",
        "anger",
        "mad",
        "furious",
        "rage",
        "outraged",
        "outrage",
        "irritated",
        "annoyed",
        "annoying",
        "frustrated",
        "frustrating",
        "frustration",
        "hate",
        "hatred",
        "resent",
        "resentment",
        "bitter",
        "bitterness",
        "hostile",
        "hostility",
        "infuriated",
        "livid",
        "enraged",
        "disgusted",
        "fed",
        "sick",
        "tired",
        "unfair",
        "wrong",
        "injustice",
        "injustices",
        "unacceptable",
        "disgusting",
        "appalling",
        "outrageous",
        "ridiculous",
        "absurd",
        "pathetic",
        "disgraceful",
        "fuming",
    },
)
_add_words(
    "fear",
    {
        "afraid",
        "fear",
        "fearful",
        "scared",
        "terrified",
        "terror",
        "panic",
        "anxious",
        "anxiety",
        "worried",
        "worry",
        "worrying",
        "nervous",
        "uneasy",
        "dread",
        "dreading",
        "horror",
        "horrible",
        "frightened",
        "frightening",
        "threatened",
        "threatening",
        "unsafe",
        "danger",
        "dangerous",
        "risk",
        "risky",
        "vulnerable",
        "insecure",
        "uncertain",
        "uncertainty",
        "overwhelmed",
        "overwhelming",
        "stress",
        "stressed",
        "stressful",
        "crisis",
        "emergency",
        "alarm",
        "alarmed",
    },
)
_add_words(
    "disgust",
    {
        "disgust",
        "disgusted",
        "disgusting",
        "revolting",
        "repulsive",
        "repulsed",
        "gross",
        "nasty",
        "vile",
        "filthy",
        "sickening",
        "nauseating",
        "awful",
        "horrible",
        "atrocious",
        "abhorrent",
        "detest",
        "detestable",
        "loathsome",
        "contempt",
        "contemptible",
        "repugnant",
        "obscene",
        "offensive",
        "shameful",
    },
)
_add_words(
    "surprise",
    {
        "surprise",
        "surprised",
        "surprising",
        "shocked",
        "shocking",
        "astonished",
        "astonishing",
        "amazed",
        "amazing",
        "unexpected",
        "sudden",
        "wow",
        "whoa",
        "unbelievable",
        "incredible",
        "stunned",
        "startled",
        "bewildered",
        "confused",
        "confusing",
        "puzzled",
        "curious",
        "curiosity",
        "wonder",
        "wondering",
    },
)
_add_words(
    "anticipation",
    {
        "anticipate",
        "anticipation",
        "expect",
        "expecting",
        "expectation",
        "await",
        "awaiting",
        "hope",
        "hoping",
        "look",
        "forward",
        "plan",
        "planning",
        "prepare",
        "preparing",
        "ready",
        "upcoming",
        "soon",
        "future",
        "goal",
        "goals",
        "aim",
        "aiming",
        "progress",
        "improve",
        "improving",
        "change",
        "changing",
        "build",
        "building",
        "develop",
        "developing",
        "learn",
        "learning",
        "grow",
        "growing",
        "potential",
        "opportunity",
        "opportunities",
        "eager",
        "eagerly",
        "excited",
    },
)


@lru_cache(maxsize=1)
def _load_lexicon() -> dict[str, dict[str, float]]:
    lexicon = {word: dict(scores) for word, scores in _BUILTIN_LEXICON.items()}
    if _LEXICON_PATH.is_file():
        with _LEXICON_PATH.open(encoding="utf-8") as handle:
            file_data = json.load(handle)
        for word, scores in file_data.items():
            normalized = word.lower()
            entry = lexicon.setdefault(normalized, {})
            for emotion, weight in scores.items():
                if emotion in NRC_EMOTIONS:
                    entry[emotion] = max(entry.get(emotion, 0.0), float(weight))
    return lexicon


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z']+", text.lower())


def score_emotions(*, text: str) -> tuple[dict[str, float], float]:
    """Return normalized emotion scores (0-1) and overall valence (-1 to 1)."""
    lexicon = _load_lexicon()
    tokens = tokenize(text)
    if not tokens:
        return {e: 0.0 for e in NRC_EMOTIONS}, 0.0

    raw: dict[str, float] = {e: 0.0 for e in NRC_EMOTIONS}
    matched = 0
    for token in tokens:
        scores = lexicon.get(token)
        if not scores:
            continue
        matched += 1
        for emotion, weight in scores.items():
            raw[emotion] += weight

    if matched == 0:
        return {e: 0.0 for e in NRC_EMOTIONS}, 0.0

    max_raw = max(raw.values()) or 1.0
    normalized = {e: round(raw[e] / max_raw, 3) for e in NRC_EMOTIONS}

    positive = normalized["joy"] + normalized["trust"] + normalized["anticipation"] * 0.5
    negative = (
        normalized["anger"] + normalized["disgust"] + normalized["fear"] + normalized["sadness"]
    )
    valence = round((positive - negative) / max(positive + negative, 1.0), 3)
    return normalized, valence


def derive_overlays(*, emotion_scores: dict[str, float]) -> dict[str, float]:
    overlays: dict[str, float] = {}
    sadness = emotion_scores.get("sadness", 0.0)
    fear = emotion_scores.get("fear", 0.0)
    anger = emotion_scores.get("anger", 0.0)
    trust = emotion_scores.get("trust", 0.0)
    joy = emotion_scores.get("joy", 0.0)
    anticipation = emotion_scores.get("anticipation", 0.0)

    if sadness >= 0.4 or fear >= 0.3:
        overlays["grief"] = round(min(1.0, sadness * 0.8 + fear * 0.3), 3)
    if anger >= 0.35 and anticipation >= 0.2:
        overlays["frustration"] = round(min(1.0, anger * 0.7 + anticipation * 0.3), 3)
    elif anger >= 0.4:
        overlays["frustration"] = round(anger * 0.6, 3)
    if anger >= 0.25 and trust >= 0.2 and anticipation >= 0.25:
        overlays["constructive_criticism"] = round(min(1.0, (anger + anticipation + trust) / 3), 3)
    if trust >= 0.35 and (joy >= 0.25 or sadness >= 0.25):
        overlays["emotional_support"] = round(min(1.0, trust * 0.6 + joy * 0.3 + sadness * 0.2), 3)
    return overlays
