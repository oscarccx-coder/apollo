# Apollo

Apollo is a local-first desktop AI assistant.

The repository has been reorganised into a clean `src/` layout. Source code, runtime state, models, and machine-specific paths are now separated instead of being mixed inside one uploaded folder.

## Layout

```text
apollo/
├─ src/
│  ├─ apollo_main.py
│  ├─ config.py
│  ├─ paths.py
│  ├─ core/
│  └─ gui/
├─ tests/
├─ run_apollo.py
└─ requirements.txt
```

Generated Python caches, runtime storage, model weights and local audio are excluded from Git.

## Apollo locations

Machine-specific locations are centralised in `src/paths.py`.

Windows defaults:

- Apollo UI/install root: `F:\Apollo\apollo 1\apollo_ui`
- LLM models: `F:\Apollo\models`
- Runtime storage: `F:\Apollo\apollo 1\apollo_ui\storage`
- XTTS voice model: `%LOCALAPPDATA%\Apollo\models\voice\xtts_v2`
- XTTS download cache: `%LOCALAPPDATA%\Apollo\downloads\coqui_tts`

Environment overrides:

```text
APOLLO_ROOT
APOLLO_MODEL_DIR
APOLLO_MODEL_PATH
APOLLO_STORAGE_DIR
APOLLO_VOICE_MODEL_DIR
APOLLO_VOICE_DOWNLOAD_DIR
```

This keeps the code usable on the main Windows machine, another PC, or a GitHub Codespace without editing Python source every time a drive or folder moves.

## Install

```powershell
python -m pip install -r requirements.txt
```

Run:

```powershell
python run_apollo.py
```

The default model filename is:

```text
qwen2.5-coder-7b-instruct-q5_k_m.gguf
```

To use another model:

```powershell
$env:APOLLO_MODEL_PATH = "F:\Apollo\models\your-model.gguf"
python run_apollo.py
```

Large model files are intentionally not stored in this repository.
