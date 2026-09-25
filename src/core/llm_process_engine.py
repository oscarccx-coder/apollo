# core/llm_process_engine.py
from __future__ import annotations

import traceback
import multiprocessing as mp
from dataclasses import dataclass
from typing import List, Optional, Any, Dict

# Child process function
def _llm_worker(conn, model_path: str, n_ctx: int, n_threads: int, n_gpu_layers: int,
                temperature: float, top_p: float, max_tokens: int):
    import traceback
    try:
        from llama_cpp import Llama

        llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=n_gpu_layers,
            n_batch=64,
            use_mmap=False,
            use_mlock=False,
            verbose=False,
        )

        # Tell parent we are ready (if parent is already gone, just exit)
        try:
            conn.send({"type": "ready"})
        except Exception:
            return

        while True:
            try:
                msg = conn.recv()
            except (EOFError, BrokenPipeError):
                # Parent went away; exit quietly
                break
            except Exception:
                break

            if not isinstance(msg, dict):
                continue

            t = msg.get("type")
            if t in ("stop", None):
                break

            if t == "gen":
                prompt = msg.get("prompt", "")
                stop = msg.get("stop", []) or []
                try:
                    out = llm(
                        prompt,
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                        stop=stop,
                    )
                    text = out["choices"][0]["text"].strip()
                    try:
                        conn.send({"type": "result", "ok": True, "text": text})
                    except Exception:
                        break
                except Exception as e:
                    try:
                        conn.send({"type": "result", "ok": False, "error": str(e)})
                    except Exception:
                        break

    except Exception:
        # Try to report fatal error, but don't crash if pipe is gone
        try:
            conn.send({"type": "fatal", "error": traceback.format_exc()})
        except Exception:
            pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


@dataclass
class GenConfig:
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 256


class LLMProcessEngine:
    """
    Runs llama.cpp in a separate process for Windows stability.
    Parent process (GUI) communicates via a Pipe.

    If llama.cpp crashes, the GUI process survives.
    """

    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        n_threads: int = 8,
        n_gpu_layers: int = 0,
        temperature: float = 0.7,
        top_p: float = 0.95,
        max_tokens: int = 256,
    ):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.n_gpu_layers = n_gpu_layers
        self.cfg = GenConfig(temperature=temperature, top_p=top_p, max_tokens=max_tokens)

        self._parent_conn, child_conn = mp.Pipe()
        self._proc = mp.Process(
            target=_llm_worker,
            args=(
                child_conn,
                self.model_path,
                self.n_ctx,
                self.n_threads,
                self.n_gpu_layers,
                self.cfg.temperature,
                self.cfg.top_p,
                self.cfg.max_tokens,
            ),
            daemon=True,
        )
        self._proc.start()

        # Wait for ready or fatal
        msg = self._parent_conn.recv()
        if msg.get("type") == "fatal":
            raise RuntimeError("LLM process failed to start:\n" + msg.get("error", "Unknown"))
        if msg.get("type") != "ready":
            raise RuntimeError(f"Unexpected LLM process message: {msg}")

    def is_alive(self) -> bool:
        return self._proc.is_alive()

    def generate(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if not self.is_alive():
            raise RuntimeError("LLM process is not alive (it likely crashed).")

        self._parent_conn.send({"type": "gen", "prompt": prompt, "stop": stop or []})
        msg = self._parent_conn.recv()

        if msg.get("type") != "result":
            raise RuntimeError(f"Unexpected response from LLM process: {msg}")

        if not msg.get("ok"):
            raise RuntimeError(msg.get("error", "Unknown generation error"))

        return msg.get("text", "")

    def close(self):
        try:
            if self.is_alive():
                self._parent_conn.send({"type": "stop"})
        except Exception:
            pass
        try:
            self._parent_conn.close()
        except Exception:
            pass
