from pathlib import Path

from apollo.core.memory.store import MemoryStore


def test_research_is_persisted_and_retrieved(tmp_path: Path):
    memory = MemoryStore(tmp_path / "memory.json")
    memory.add_research(
        "fusion power",
        "Fusion combines light nuclei and requires confinement.",
    )
    hits = memory.get_relevant_research(
        "How does fusion confinement work?"
    )
    assert hits
    assert hits[0]["topic"] == "fusion power"
