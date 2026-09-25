# Apollo

Apollo is a local-first desktop AI assistant.

The repository now uses a clean `src/` layout so source code, runtime state, models, and machine-specific paths are separated.

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

## Chat behaviour

Apollo understands ordinary chat plus explicit research-style requests.

Examples:

```text
research fusion power
please investigate sodium-ion batteries
learn about the Casimir effect
look into local LLM quantisation
```

A research request runs several local-model passes:

1. fundamentals and terminology
2. practical uses and constraints
3. a skeptical/critical check
4. synthesis into one compact durable memory note

Apollo stores the compact note instead of dumping every research pass into chat. The user gets a short completion message, and later relevant questions can automatically reuse the learned note.

This is **local model research**, not internet verification. The research prompts explicitly prohibit invented citations and preserve uncertainty so a future web-research provider can be added cleanly.

Apollo's normal personality now includes occasional dry, light sarcasm. It is deliberately disabled for serious, medical, safety-critical or distressing situations.

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

This keeps the code usable on the main Windows machine, another PC, or a GitHub Codespace without editing Python source whenever a drive or folder changes.

## Install

```powershell
python -m pip install -r requirements.txt
python run_apollo.py
```

The default model filename is:

```text
qwen2.5-coder-7b-instruct-q5_k_m.gguf
```

Large model files, generated caches, runtime storage and local voice audio are intentionally not stored in this repository.
