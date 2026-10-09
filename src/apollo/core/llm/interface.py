from __future__ import annotations

from typing import List, Optional

from apollo.core.llm.process_engine import LLMProcessEngine


class LLMEngine:
    def __init__(
        self,
        model_path: str,
        n_ctx: int,
        n_threads: int,
        n_gpu_layers: int,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ):
        self._engine = LLMProcessEngine(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=n_gpu_layers,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )

    def generate(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
    ) -> str:
        return self._engine.generate(prompt, stop=stop)

    def close(self) -> None:
        self._engine.close()
