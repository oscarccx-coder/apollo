from pathlib import Path


def test_worker_source_has_bounded_waits():
    source = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "apollo"
        / "core"
        / "llm"
        / "process_engine.py"
    ).read_text(encoding="utf-8")

    assert "poll(self.startup_timeout)" in source
    assert "poll(self.generation_timeout)" in source
    assert "self._proc.join(timeout=2.0)" in source
    assert "self._proc.terminate()" in source
    assert 'mp.get_context("spawn")' in source
