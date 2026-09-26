from __future__ import annotations
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class ChatIntent:
    kind: str
    target: str = ""

_RESEARCH_PATTERNS = (
    re.compile(r"^\s*(?:please\s+)?research\s*:?\s+(.+?)\s*$", re.IGNORECASE),
    re.compile(r"^\s*(?:please\s+)?(?:investigate|study|learn\s+about|look\s+into)\s*:?\s+(.+?)\s*$", re.IGNORECASE),
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
