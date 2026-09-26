from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Optional

RESEARCH_ANGLES = (
    ("fundamentals", "Explain the core concepts, terminology, mechanisms and assumptions. Separate well-established ideas from uncertain or disputed claims."),
    ("practical", "Explore practical uses, implementation approaches, constraints, trade-offs and concrete examples."),
    ("critical_check", "Act as a skeptical reviewer. Look for failure modes, contradictions, common misconceptions, missing context and claims that should be verified externally."),
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

### Research topic
{topic}

### Research angle
{angle_name}: {instruction}

Return dense working notes for Apollo. Do not address the user directly.
### Apollo Research Notes
"""

def _synthesis_prompt(topic: str, findings: Dict[str, str]) -> str:
    blocks = [f"## {name}\n{text.strip()}" for name, text in findings.items()]
    joined = "\n\n".join(blocks)
    return f"""### System
You are Apollo's research memory compiler.
Compress several local-model research passes into one durable knowledge note.
Keep useful facts, mechanisms, constraints, caveats and unresolved questions.
Remove repetition and fluff.
Do not invent citations or claim web verification.
Keep the result under about 700 words.

### Topic
{topic}

### Working passes
{joined}

### Durable Apollo Knowledge Note
"""

def run_local_research(engine, topic: str, progress: Optional[Callable[[str], None]] = None) -> ResearchResult:
    topic = str(topic or "").strip()
    if not topic:
        raise ValueError("Research topic is empty.")
    findings: Dict[str, str] = {}
    total = len(RESEARCH_ANGLES)
    for index, (name, instruction) in enumerate(RESEARCH_ANGLES, start=1):
        if progress:
            progress(f"Research pass {index}/{total}: {name.replace('_', ' ')}")
        findings[name] = engine.generate(
            _angle_prompt(topic, name, instruction),
            stop=["### User", "### System", "### Research topic"],
        ).strip()
    if progress:
        progress("Compiling useful knowledge and removing repetition")
    summary = engine.generate(
        _synthesis_prompt(topic, findings),
        stop=["### User", "### System", "### Research topic"],
    ).strip()
    if not summary:
        raise RuntimeError("Research synthesis returned no usable knowledge.")
    return ResearchResult(topic=topic, summary=summary, findings=findings)

def completion_message(topic: str) -> str:
    return (
        f"Done — I've expanded my local working knowledge of {topic}. "
        "I checked it from a few different angles, compressed the useful bits, "
        "and stored the result. No information avalanche. Revolutionary, apparently."
    )
