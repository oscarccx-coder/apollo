# Apollo architecture

Application source lives under `src/apollo/`.

- `core/llm/`: isolated llama.cpp process and interface
- `core/memory/`: persistent local memory
- `intelligence/`: personality, intent parsing and research workflows
- `ui/`: PyQt interface only
- `scripts/updates/`: update/install/migration scripts
- `scripts/dev/`: developer-only maintenance utilities

Runtime models, storage, caches and downloaded update payloads are not source code and should not be committed.
