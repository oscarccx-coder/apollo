from pathlib import Path

from apollo import paths


def test_runtime_paths_are_paths():
    for value in (
        paths.APOLLO_ROOT,
        paths.MODEL_DIR,
        paths.STORAGE_DIR,
        paths.VOICE_MODEL_DIR,
        paths.VOICE_DOWNLOAD_DIR,
        paths.MEMORY_FILE,
        paths.UPDATE_DIR,
    ):
        assert isinstance(value, Path)


def test_runtime_children_live_under_storage():
    assert paths.MEMORY_FILE == paths.STORAGE_DIR / "memory.json"
    assert paths.LOG_DIR == paths.STORAGE_DIR / "logs"
    assert paths.CACHE_DIR == paths.STORAGE_DIR / "cache"
    assert paths.BACKUP_DIR == paths.STORAGE_DIR / "backups"
    assert paths.UPDATE_DIR == paths.STORAGE_DIR / "updates"
