from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional


# Apollo deliberately attacks a research request from different directions.
# These are local-model passes today; external/web providers can be added later
# without changing the chat command contract.
RESEARCH_ANGLES = (
    (
        "fundamentals",
        "Explain the core concepts, terminology, mechanisms and assumptions. "
        "Separate well-established ideas from uncertain or disputed claims.",
    ),
    (
        "implementation",
        "Explore how this works in practice: implementation approaches, tools, "
        "requirements, bottlenecks, costs and failure points.",
    ),
    (
        "alternatives",
        "Compare alternative approaches, competing explanations or adjacent "
        "methods. Note when one option is better suited to a particular use.",
    ),
    (
        "critical_check",
        "Act as a skeptical reviewer. Look for contradictions, common "
        "misconceptions, missing context, edge cases and claims that should "
        "be verified externally.",
    ),
)


@dataclass
class ResearchResult:
    topic: str
    summary: str
    findings: Dict[str, str]
    method: str = "local_multi_pass"


def _angle_prompt(topic: str, angle_name: str, instruction: str) -> str:
    return f"""### System
You are Apollo's local research worker.
Work carefully and do not invent sources, links, experiments, statistics or citations.
This is local model analysis, not web research.
If a point is uncertain, label it uncertain.
Do not write a user-facing answer yet. You are building Apollo's own knowledge.

### Research topic
{topic}

### Research angle
{angle_name}: {instruction}

Return dense working notes for Apollo.
### Apollo Research Notes
"""


def _synthesis_prompt(topic: str, findings: Dict[str, str]) -> str:
    blocks = [
        f"## {name}\n{text.strip()}"
        for name, text in findings.items()
        if text.strip()
    ]
    joined = "\n\n".join(blocks)

    return f"""### System
You are Apollo's research memory compiler.
Combine several independent local-model research passes into one durable knowledge note.
Keep useful facts, mechanisms, constraints, alternatives, caveats and unresolved questions.
Remove repetition, weak speculation and conversational filler.
Where the passes disagree, preserve that disagreement instead of pretending certainty.
Do not invent citations or claim web verification.
Keep the result under about 700 words.

### Topic
{topic}

### Working passes
{joined}

### Durable Apollo Knowledge Note
"""


def run_local_research(
    engine,
    topic: str,
    progress: Optional[Callable[[str], None]] = None,
) -> ResearchResult:
    topic = str(topic or "").strip()
    if not topic:
        raise ValueError("Research topic is empty.")

    findings: Dict[str, str] = {}
    total = len(RESEARCH_ANGLES)

    for index, (name, instruction) in enumerate(RESEARCH_ANGLES, start=1):
        if progress:
            progress(
                f"Research pass {index}/{total}: "
                f"{name.replace('_', ' ')}"
            )

        findings[name] = engine.generate(
            _angle_prompt(topic, name, instruction),
            stop=["### User", "### System", "### Research topic"],
        ).strip()

    if progress:
        progress("Cross-checking the passes and compressing useful knowledge")

    summary = engine.generate(
        _synthesis_prompt(topic, findings),
        stop=["### User", "### System", "### Research topic"],
    ).strip()

    if not summary:
        raise RuntimeError(
            "Research synthesis returned no usable knowledge."
        )

    return ResearchResult(
        topic=topic,
        summary=summary,
        findings=findings,
    )


def completion_message(topic: str) -> str:
    return (
        f"Completed. I've expanded my knowledge of {topic} and stored the "
        "useful parts for later. I checked it from several angles instead "
        "of trusting the first answer that wandered past. Miraculous restraint."
    )
