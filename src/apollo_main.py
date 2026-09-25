from __future__ import annotations

from pathlib import Path
import multiprocessing as mp

import config
from core.llm_interface import LLMEngine
from core.memory_core import MemoryStore
from paths import ensure_runtime_dirs


def build_engine_and_memory():
    ensure_runtime_dirs()

    model_path = Path(config.MODEL_PATH).expanduser()
    if not model_path.is_file():
        raise FileNotFoundError(
            "Apollo model was not found.\n"
            f"Expected: {model_path}\n"
            "Set APOLLO_MODEL_PATH to override the model location."
        )

    memory = MemoryStore(config.MEMORY_FILE)
    engine = LLMEngine(
        model_path=str(model_path),
        n_ctx=config.N_CTX,
        n_threads=config.N_THREADS,
        n_gpu_layers=config.N_GPU_LAYERS,
        temperature=config.TEMPERATURE,
        top_p=config.TOP_P,
        max_tokens=config.MAX_TOKENS,
    )
    return engine, memory


def main():
    mp.freeze_support()
    engine, memory = build_engine_and_memory()

    from gui.apollo_gui import run_gui

    run_gui(
        engine=engine,
        memory=memory,
        app_title=config.APP_TITLE,
        max_turns_in_context=config.MAX_TURNS_IN_CONTEXT,
    )


if __name__ == "__main__":
    main()
