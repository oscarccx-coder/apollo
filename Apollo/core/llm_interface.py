# core/llm_interface.py
from core.llm_process_engine import LLMProcessEngine

class LLMEngine:
    def __init__(self, model_path: str, n_ctx: int, n_threads: int, n_gpu_layers: int,
                 temperature: float, top_p: float, max_tokens: int):
        self._e = LLMProcessEngine(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=n_gpu_layers,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )

    def generate(self, prompt: str, stop=None) -> str:
        return self._e.generate(prompt, stop=stop)

    def close(self):
        self._e.close()
