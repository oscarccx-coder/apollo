# Apollo

Apollo is a local-first desktop AI assistant.

The repository now uses a proper Python package layout so runtime state, models, update payloads and application source stop living in the same digital junk drawer.

## Layout

```text
apollo/
├─ src/
│  └─ apollo/
│     ├─ app.py
│     ├─ config.py
│     ├─ paths.py
│     ├─ core/
│     │  ├─ llm/
│     │  └─ memory/
│     ├─ intelligence/
│     └─ ui/
├─ tests/
├─ docs/
├─ scripts/
│  ├─ dev/
│  └─ updates/
├─ run_apollo.py
├─ pyproject.toml
└─ requirements.txt
```

### Folder responsibilities

- `core/llm/`: llama.cpp process isolation and public LLM interface
- `core/memory/`: persistent local memory
- `intelligence/`: personality, intent parsing and research workflows
- `ui/`: PyQt interface
- `scripts/updates/`: update/install/migration scripts
- `scripts/dev/`: developer maintenance tools
- `docs/`: architecture and developer documentation

## Chat research

Apollo understands commands such as:

```text
research fusion power
please investigate sodium-ion batteries
learn about the Casimir effect
look into local LLM quantisation
```

Research runs several local-model passes and stores a compact knowledge note. Chat receives a short completion message rather than every scratchpad result.

This is local-model analysis, not web verification.

## Personality

Apollo uses occasional dry/light sarcasm during ordinary conversation, while serious, medical and safety-critical situations stay direct.

## Windows paths

Centralised in `src/apollo/paths.py`:

- Apollo root: `F:\Apollo\apollo 1\apollo_ui`
- LLM models: `F:\Apollo\models`
- Storage: `F:\Apollo\apollo 1\apollo_ui\storage`
- XTTS model: `%LOCALAPPDATA%\Apollo\models\voice\xtts_v2`
- XTTS download cache: `%LOCALAPPDATA%\Apollo\downloads\coqui_tts`

Environment overrides remain available through `APOLLO_ROOT`, `APOLLO_MODEL_DIR`, `APOLLO_MODEL_PATH`, `APOLLO_STORAGE_DIR`, `APOLLO_VOICE_MODEL_DIR` and `APOLLO_VOICE_DOWNLOAD_DIR`.

## Run

```powershell
python -m pip install -r requirements.txt
python run_apollo.py
```
