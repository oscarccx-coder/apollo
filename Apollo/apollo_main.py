# apollo_main.py
from pathlib import Path
import multiprocessing as mp

import config
from core.llm_interface import LLMEngine
from core.memory_core import MemoryStore


def ensure_dirs():
    Path("storage").mkdir(exist_ok=True)


def build_engine_and_memory():
    ensure_dirs()

    model_path = Path(config.MODEL_PATH)
    if not model_path.exists():
        raise FileNotFoundError(f"MODEL_PATH not found:\n  {config.MODEL_PATH}")

    memory = MemoryStore(config.MEMORY_FILE)

    # Keep conservative while stabilising
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
    engine, memory = build_engine_and_memory()

    from gui.apollo_gui import run_gui
    run_gui(
        engine=engine,
        memory=memory,
        app_title=config.APP_TITLE,
        max_turns_in_context=config.MAX_TURNS_IN_CONTEXT
    )


if __name__ == "__main__":
    mp.freeze_support()
    main()
