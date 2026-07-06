import re

HOSTILE_PATTERNS = [
    r"\b(stupid|idiot|dumb|worthless|moron|imbecile|loser)\b",
    r"\b(shut up|go away|get lost)\b",
    r"\b(hate you|despise you)\b",
]

DEHUMANIZATION_PATTERNS = [
    r"\b(subhuman|vermin|scum|parasite|animal)\b",
    r"\b(not (even )?human|less than human)\b",
]

THREAT_PATTERNS = [
    r"\b(i('ll| will) (kill|hurt|destroy|ruin) you)\b",
    r"\b(you('re| are) (dead|finished|done))\b",
    r"\b(watch your back)\b",
]


def detect_conduct_flags(*, text: str) -> list[str]:
    lower = text.lower()
    flags: list[str] = []
    if any(re.search(p, lower) for p in HOSTILE_PATTERNS):
        flags.append("hostile_language")
    if any(re.search(p, lower) for p in DEHUMANIZATION_PATTERNS):
        flags.append("dehumanization")
    if any(re.search(p, lower) for p in THREAT_PATTERNS):
        flags.append("threat")
    return flags
