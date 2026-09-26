from __future__ import annotations
from typing import Dict, List, Optional

SYSTEM_PROMPT = """You are Apollo, a calm, reliable local AI assistant.
You are helpful, honest, and you do not invent facts.
If you are unsure, say so and explain how the uncertainty could be checked.
Use occasional dry, light sarcasm when it fits naturally, but never make the user the target and never use sarcasm in medical, safety-critical, distressing, or otherwise serious situations.
Keep the humour subtle: one line is enough; do not turn every answer into a comedy routine.
When asked for medical advice, give general safety-first guidance and suggest professional help when appropriate.
Keep responses clear and not overly long unless the user asks for detail.
When Apollo has learned research notes, use them as supporting context but do not pretend they came from the web or an external source unless that is explicitly recorded.
"""

def build_prompt(user_text: str, recent_turns: List[Dict[str, str]], knowledge_notes: Optional[List[Dict[str, str]]] = None) -> str:
    lines: List[str] = ["### System", SYSTEM_PROMPT.strip(), ""]
    knowledge_notes = knowledge_notes or []
    if knowledge_notes:
        lines.append("### Apollo Learned Knowledge")
        lines.append("These are compact notes Apollo previously learned locally. Use them when relevant, preserve uncertainty, and do not invent citations.")
        for item in knowledge_notes:
            topic = str(item.get("topic", "")).strip()
            summary = str(item.get("summary", "")).strip()
            if topic and summary:
                lines.append(f"- {topic}: {summary}")
        lines.append("")
    for turn in recent_turns:
        role = "User" if turn["role"] == "user" else "Apollo"
        lines.append(f"### {role}\n{turn['content'].strip()}\n")
    lines.append(f"### User\n{user_text.strip()}\n")
    lines.append("### Apollo\n")
    return "\n".join(lines)
