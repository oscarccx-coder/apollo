from __future__ import annotations

import os
from pathlib import Path

from paths import MEMORY_FILE, MODEL_DIR


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


MODEL_FILENAME = os.environ.get(
    "APOLLO_MODEL_FILENAME",
    "qwen2.5-coder-7b-instruct-q5_k_m.gguf",
)

MODEL_PATH = Path(
    os.environ.get("APOLLO_MODEL_PATH")
    or (MODEL_DIR / MODEL_FILENAME)
)

N_THREADS = _env_int("APOLLO_N_THREADS", min(8, os.cpu_count() or 4))
N_GPU_LAYERS = _env_int("APOLLO_N_GPU_LAYERS", 20)
N_CTX = _env_int("APOLLO_N_CTX", 4096)

MAX_TOKENS = _env_int("APOLLO_MAX_TOKENS", 512)
TEMPERATURE = _env_float("APOLLO_TEMPERATURE", 0.7)
TOP_P = _env_float("APOLLO_TOP_P", 0.95)

MAX_TURNS_IN_CONTEXT = _env_int("APOLLO_MAX_TURNS_IN_CONTEXT", 10)
APP_TITLE = os.environ.get("APOLLO_APP_TITLE", "Apollo")

MEMORY_FILE = Path(MEMORY_FILE)
