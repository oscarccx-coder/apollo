from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from core.chat_intents import parse_chat_intent

def test_research_commands():
    assert parse_chat_intent("research fusion power").kind == "research"
    assert parse_chat_intent("research fusion power").target == "fusion power"
    assert parse_chat_intent("please investigate battery chemistry").target == "battery chemistry"
    assert parse_chat_intent("learn about Casimir effect").target == "Casimir effect"

def test_normal_chat_is_not_hijacked():
    assert parse_chat_intent("What is research methodology?").kind == "chat"
    assert parse_chat_intent("Can you explain fusion?").kind == "chat"
