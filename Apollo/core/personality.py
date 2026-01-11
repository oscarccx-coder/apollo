# core/personality.py
from __future__ import annotations
from typing import List, Dict

SYSTEM_PROMPT = """You are Apollo, a calm, reliable assistant.
You are helpful, honest, and you do not invent facts.
If you are unsure, you say so and suggest how to verify.
When asked for medical advice, you give general safety-first guidance and suggest professional help when appropriate.
Keep responses clear and not overly long unless the user asks for detail.
"""

def build_prompt(user_text: str, recent_turns: List[Dict[str, str]]) -> str:
    """
    Build a single text prompt for llama.cpp.
    Simple format to avoid template issues.
    """
    lines: List[str] = []
    lines.append("### System")
    lines.append(SYSTEM_PROMPT.strip())
    lines.append("")

    for t in recent_turns:
        role = "User" if t["role"] == "user" else "Apollo"
        lines.append(f"### {role}\n{t['content'].strip()}\n")

    lines.append(f"### User\n{user_text.strip()}\n")
    lines.append("### Apollo\n")
    return "\n".join(lines)
