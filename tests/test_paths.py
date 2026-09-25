from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

import paths


def test_runtime_paths_are_paths():
    for value in (
        paths.APOLLO_ROOT,
        paths.MODEL_DIR,
        paths.STORAGE_DIR,
        paths.VOICE_MODEL_DIR,
        paths.VOICE_DOWNLOAD_DIR,
        paths.MEMORY_FILE,
    ):
        assert isinstance(value, Path)


def test_memory_file_lives_in_storage():
    assert paths.MEMORY_FILE == paths.STORAGE_DIR / "memory.json"
