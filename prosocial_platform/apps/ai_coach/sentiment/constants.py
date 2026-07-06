NRC_EMOTIONS = (
    "anger",
    "anticipation",
    "disgust",
    "fear",
    "joy",
    "sadness",
    "surprise",
    "trust",
)

OVERLAY_EMOTIONS = (
    "grief",
    "frustration",
    "constructive_criticism",
    "emotional_support",
)

CONDUCT_FLAGS = (
    "hostile_language",
    "dehumanization",
    "threat",
)

EMOTION_LABELS = {
    "anger": "Anger",
    "anticipation": "Anticipation",
    "disgust": "Disgust",
    "fear": "Fear",
    "joy": "Joy",
    "sadness": "Sadness",
    "surprise": "Surprise",
    "trust": "Trust",
    "grief": "Grief",
    "frustration": "Frustration",
    "constructive_criticism": "Constructive criticism",
    "emotional_support": "Emotional support",
}

CONDUCT_LABELS = {
    "hostile_language": "Phrasing may come across as hostile",
    "dehumanization": "Language may dehumanize others",
    "threat": "Language may read as threatening",
}

MODEL_VERSION_LEXICON = "nrc-v1"
MODEL_VERSION_LEXICON_LLM = "nrc-v1+llm"

CONTENT_REVIEW_MIN_LENGTH = 8
