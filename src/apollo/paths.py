from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR.parent
PROJECT_ROOT = SRC_DIR.parent


def _env_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else Path(default)


def _windows_default(path: str, fallback: Path) -> Path:
    return Path(path) if os.name == "nt" else fallback


APOLLO_ROOT = _env_path(
    "APOLLO_ROOT",
    _windows_default(r"F:\Apollo\apollo 1\apollo_ui", PROJECT_ROOT),
)
MODEL_DIR = _env_path(
    "APOLLO_MODEL_DIR",
    _windows_default(r"F:\Apollo\models", PROJECT_ROOT / "models"),
)
STORAGE_DIR = _env_path("APOLLO_STORAGE_DIR", APOLLO_ROOT / "storage")

LOCALAPPDATA = Path(
    os.environ.get("LOCALAPPDATA") or (Path.home() / ".local" / "share")
)
VOICE_MODEL_DIR = _env_path(
    "APOLLO_VOICE_MODEL_DIR",
    LOCALAPPDATA / "Apollo" / "models" / "voice" / "xtts_v2",
)
VOICE_DOWNLOAD_DIR = _env_path(
    "APOLLO_VOICE_DOWNLOAD_DIR",
    LOCALAPPDATA / "Apollo" / "downloads" / "coqui_tts",
)

MEMORY_FILE = STORAGE_DIR / "memory.json"
LOG_DIR = STORAGE_DIR / "logs"
CACHE_DIR = STORAGE_DIR / "cache"
BACKUP_DIR = STORAGE_DIR / "backups"
UPDATE_DIR = STORAGE_DIR / "updates"


def ensure_runtime_dirs() -> None:
    for folder in (
        STORAGE_DIR,
        LOG_DIR,
        CACHE_DIR,
        BACKUP_DIR,
        UPDATE_DIR,
    ):
        folder.mkdir(parents=True, exist_ok=True)
