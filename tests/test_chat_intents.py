from apollo.intelligence.intents import parse_chat_intent


def test_research_commands():
    cases = {
        "research fusion power": "fusion power",
        "reasearch fusion power": "fusion power",
        "reseach fusion power": "fusion power",
        "reserch fusion power": "fusion power",
        "research about fusion power": "fusion power",
        "research on fusion power": "fusion power",
        "please investigate battery chemistry": "battery chemistry",
        "learn about Casimir effect": "Casimir effect",
        "look into local LLM quantisation": "local LLM quantisation",
        "find out about sodium ion batteries": "sodium ion batteries",
    }

    for command, target in cases.items():
        intent = parse_chat_intent(command)
        assert intent.kind == "research"
        assert intent.target == target


def test_normal_chat_is_not_hijacked():
    assert parse_chat_intent("What is research methodology?").kind == "chat"
    assert parse_chat_intent("Can you explain fusion?").kind == "chat"
    assert parse_chat_intent("I researched this yesterday").kind == "chat"
