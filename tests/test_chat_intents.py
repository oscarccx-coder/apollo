from apollo.intelligence.intents import parse_chat_intent


def test_research_commands():
    assert parse_chat_intent("research fusion power").kind == "research"
    assert parse_chat_intent("research fusion power").target == "fusion power"
    assert (
        parse_chat_intent("please investigate battery chemistry").target
        == "battery chemistry"
    )
    assert parse_chat_intent("learn about Casimir effect").target == "Casimir effect"


def test_normal_chat_is_not_hijacked():
    assert parse_chat_intent("What is research methodology?").kind == "chat"
    assert parse_chat_intent("Can you explain fusion?").kind == "chat"
