from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from core.memory_core import MemoryStore

def test_research_is_persisted_and_retrieved():
    with tempfile.TemporaryDirectory() as td:
        memory = MemoryStore(Path(td) / "memory.json")
        memory.add_research("fusion power", "Fusion combines light nuclei and requires confinement.")
        hits = memory.get_relevant_research("How does fusion confinement work?")
        assert hits
        assert hits[0]["topic"] == "fusion power"
