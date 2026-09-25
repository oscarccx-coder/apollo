from __future__ import annotations
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

@dataclass
class Turn:
    role: str
    content: str
    ts: str

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

class MemoryStore:
    """Persistent store for conversation, notes and locally learned research."""
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.data: Dict[str, Any] = {"turns": [], "notes": [], "research": []}
        self._load()

    def _load(self):
        if self.filepath.exists():
            try:
                loaded = json.loads(self.filepath.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    self.data = loaded
            except Exception:
                backup = self.filepath.with_suffix(".corrupt.json")
                backup.write_text(self.filepath.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        self.data.setdefault("turns", [])
        self.data.setdefault("notes", [])
        self.data.setdefault("research", [])
        self._save()

    def _save(self):
        payload = json.dumps(self.data, ensure_ascii=False, indent=2)
        temp = self.filepath.with_suffix(self.filepath.suffix + ".tmp")
        temp.write_text(payload, encoding="utf-8")
        temp.replace(self.filepath)

    def add_turn(self, role: str, content: str):
        self.data["turns"].append(asdict(Turn(role=role, content=content, ts=_utc_now())))
        self._save()

    def get_last_turns(self, n: int) -> List[Dict[str, str]]:
        return [{"role": t["role"], "content": t["content"]} for t in self.data.get("turns", [])[-n:] if "role" in t and "content" in t]

    def add_note(self, note: str):
        self.data.setdefault("notes", []).append({"note": str(note), "ts": _utc_now()})
        self._save()

    def get_notes(self) -> List[Dict[str, str]]:
        return list(self.data.get("notes", []))

    def add_research(self, topic: str, summary: str, *, method: str = "local_multi_pass") -> Dict[str, str]:
        entry = {"topic": str(topic).strip(), "summary": str(summary).strip(), "method": str(method), "ts": _utc_now()}
        self.data.setdefault("research", []).append(entry)
        self._save()
        return entry

    def get_research(self) -> List[Dict[str, str]]:
        return list(self.data.get("research", []))

    @staticmethod
    def _keywords(text: str) -> set[str]:
        words = re.findall(r"[a-zA-Z0-9_'-]{3,}", str(text).lower())
        stop = {"the","and","for","with","that","this","from","what","when","where","which","about","into","have","your","you","are"}
        return {word for word in words if word not in stop}

    def get_relevant_research(self, query: str, limit: int = 3) -> List[Dict[str, str]]:
        query_words = self._keywords(query)
        if not query_words:
            return []
        ranked = []
        for index, entry in enumerate(self.data.get("research", [])):
            topic_words = self._keywords(entry.get("topic", ""))
            summary_words = self._keywords(entry.get("summary", ""))
            score = (3 * len(query_words & topic_words)) + len(query_words & summary_words)
            if score:
                ranked.append((score, index, entry))
        ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [dict(item[2]) for item in ranked[: max(0, int(limit))]]
