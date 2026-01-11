# core/memory_core.py
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class Turn:
    role: str  # "user" | "assistant"
    content: str
    ts: str

class MemoryStore:
    """
    Simple persistent memory:
    - Stores full chat turns in JSON.
    - Provides last N turns for short-term context.
    You can later upgrade this to embeddings / vector DB, etc.
    """
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.data: Dict[str, Any] = {"turns": [], "notes": []}
        self._load()

    def _load(self):
        if self.filepath.exists():
            try:
                self.data = json.loads(self.filepath.read_text(encoding="utf-8"))
            except Exception:
                # If corrupted, keep a backup and start fresh.
                backup = self.filepath.with_suffix(".corrupt.json")
                backup.write_text(self.filepath.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                self.data = {"turns": [], "notes": []}
                self._save()
        else:
            self._save()

    def _save(self):
        self.filepath.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_turn(self, role: str, content: str):
        t = Turn(role=role, content=content, ts=datetime.utcnow().isoformat() + "Z")
        self.data["turns"].append(asdict(t))
        self._save()

    def get_last_turns(self, n: int) -> List[Dict[str, str]]:
        turns = self.data.get("turns", [])[-n:]
        return [{"role": t["role"], "content": t["content"]} for t in turns]

    def add_note(self, note: str):
        self.data.setdefault("notes", []).append(
            {"note": note, "ts": datetime.utcnow().isoformat() + "Z"}
        )
        self._save()

    def get_notes(self) -> List[Dict[str, str]]:
        return self.data.get("notes", [])
