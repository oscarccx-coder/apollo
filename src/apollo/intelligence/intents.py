from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ChatIntent:
    kind: str
    target: str = ""


# Deliberately accept a few common misspellings because command routing should
# understand the human, not demand that the human pass a spelling exam first.
_RESEARCH_VERB = (
    r"(?:research|reasearch|reseach|reserch|investigate|study|"
    r"learn\s+about|look\s+into|find\s+out\s+about)"
)

_RESEARCH_PATTERNS = (
    re.compile(
        rf"^\s*(?:please\s+)?{_RESEARCH_VERB}"
        rf"(?:\s+(?:about|on))?\s*:?\s+(.+?)\s*$",
        re.IGNORECASE,
    ),
)


def parse_chat_intent(text: str) -> ChatIntent:
    raw = str(text or "").strip()
    if not raw:
        return ChatIntent("chat")

    for pattern in _RESEARCH_PATTERNS:
        match = pattern.match(raw)
        if match:
            target = match.group(1).strip(" .,:;!?")
            if target:
                return ChatIntent("research", target)

    return ChatIntent("chat")
