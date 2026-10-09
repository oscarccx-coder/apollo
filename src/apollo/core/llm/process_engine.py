from __future__ import annotations

import multiprocessing as mp
import threading
import traceback
from dataclasses import dataclass
from typing import List, Optional


def _llm_worker(
    conn,
    model_path: str,
    n_ctx: int,
    n_threads: int,
    n_gpu_layers: int,
    temperature: float,
    top_p: float,
    max_tokens: int,
) -> None:
    try:
        from llama_cpp import Llama

        llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=n_gpu_layers,
            n_batch=64,
            use_mmap=True,
            use_mlock=False,
            verbose=False,
        )
        conn.send({"type": "ready"})

        while True:
            try:
                msg = conn.recv()
            except (EOFError, BrokenPipeError):
                break

            if not isinstance(msg, dict):
                continue

            kind = msg.get("type")
            if kind in ("stop", None):
                break
            if kind != "gen":
                continue

            try:
                out = llm(
                    msg.get("prompt", ""),
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    stop=msg.get("stop", []) or [],
                )
                text = out["choices"][0]["text"].strip()
                conn.send({"type": "result", "ok": True, "text": text})
            except Exception as exc:
                conn.send({
                    "type": "result",
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                })

    except Exception:
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
    """Run llama.cpp outside the GUI process with bounded waits."""

    def __init__(
        self,
        model_path: str,
        n_ctx: int = 4096,
        n_threads: int = 8,
        n_gpu_layers: int = 20,
        temperature: float = 0.7,
        top_p: float = 0.95,
        max_tokens: int = 512,
        startup_timeout: float = 120.0,
        generation_timeout: float = 600.0,
    ):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.n_gpu_layers = n_gpu_layers
        self.cfg = GenConfig(temperature, top_p, max_tokens)
        self.startup_timeout = float(startup_timeout)
        self.generation_timeout = float(generation_timeout)
        self._io_lock = threading.Lock()
        self._closed = False

        ctx = mp.get_context("spawn")
        self._parent_conn, child_conn = ctx.Pipe()
        self._proc = ctx.Process(
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
            name="ApolloLLMWorker",
        )
        self._proc.start()
        child_conn.close()

        if not self._parent_conn.poll(self.startup_timeout):
            self.close(force=True)
            raise TimeoutError(
                f"LLM worker did not become ready within "
                f"{self.startup_timeout:.0f}s."
            )

        msg = self._parent_conn.recv()
        if msg.get("type") == "fatal":
            self.close(force=True)
            raise RuntimeError(
                "LLM process failed to start:\n"
                + msg.get("error", "Unknown worker error")
            )
        if msg.get("type") != "ready":
            self.close(force=True)
            raise RuntimeError(f"Unexpected LLM worker message: {msg}")

    def is_alive(self) -> bool:
        return not self._closed and self._proc.is_alive()

    def generate(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
    ) -> str:
        with self._io_lock:
            if not self.is_alive():
                raise RuntimeError("LLM worker is not alive.")

            self._parent_conn.send({
                "type": "gen",
                "prompt": prompt,
                "stop": stop or [],
            })

            if not self._parent_conn.poll(self.generation_timeout):
                self.close(force=True)
                raise TimeoutError(
                    "LLM generation timed out and the worker was stopped "
                    "instead of freezing Apollo indefinitely."
                )

            msg = self._parent_conn.recv()
            if msg.get("type") == "fatal":
                raise RuntimeError(
                    "LLM worker failed:\n"
                    + msg.get("error", "Unknown worker error")
                )
            if msg.get("type") != "result":
                raise RuntimeError(
                    f"Unexpected response from LLM worker: {msg}"
                )
            if not msg.get("ok"):
                raise RuntimeError(
                    msg.get("error", "Unknown generation error")
                )
            return msg.get("text", "")

    def close(self, force: bool = False) -> None:
        if self._closed:
            return
        self._closed = True

        try:
            if self._proc.is_alive() and not force:
                self._parent_conn.send({"type": "stop"})
                self._proc.join(timeout=2.0)
        except Exception:
            pass

        try:
            if self._proc.is_alive():
                self._proc.terminate()
                self._proc.join(timeout=2.0)
        except Exception:
            pass

        try:
            self._parent_conn.close()
        except Exception:
            pass
