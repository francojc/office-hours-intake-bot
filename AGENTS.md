# Office Hours Intake Bot

AI-powered student intake chatbot for Cal.com office hours appointments.
Runs locally on Mac Mini M4 with Gemma 4 31B via Ollama.

## Quick Reference

```bash
# Full environment setup (model, RAG index, deps)
./scripts/setup-environment.sh

# Install dependencies only
uv sync

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Lint and format
uv run ruff check app/ tests/
uv run ruff format app/ tests/

# Pull the LLM model
ollama pull gemma4:31b

# Expose via Tailscale Funnel (HTTPS :8443 → localhost:8000)
tailscale funnel --bg --https 8443 8000
```

## Project Structure

```
office-hours-intake-bot/
├── app/                   # FastAPI application source
│   ├── main.py            # Entry point and route mounting
│   ├── chat.py            # Ollama-backed conversation engine
│   ├── rag.py             # LlamaIndex + ChromaDB RAG pipeline
│   ├── summary.py         # Pydantic models for intake summary schema
│   ├── delivery.py        # Email and Cal.com API summary delivery
│   ├── webhooks.py        # Cal.com webhook handlers
│   └── config.py          # Settings and environment variables
├── rag-corpus/            # Course materials for RAG indexing
│   ├── spa212/            # SPA 212-T syllabus, assignments, topics
│   └── general/           # Office hours scope, referral resources
├── chroma_db/             # ChromaDB persistent store (gitignored)
├── training-data/         # Fine-tuning JSONL files (deferred)
├── static/                # Chat widget HTML/CSS/JS
├── scripts/               # Environment setup and maintenance scripts
├── tests/                 # pytest test suite
├── specs/                 # Planning, progress, implementation docs
├── logs/                  # Weekly reviews and session logs
├── pyproject.toml         # Dependencies and project metadata
└── uv.lock               # Locked dependency versions
```

## Tech Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI + Uvicorn
- **LLM:** Gemma 4 31B via Ollama (http://mac-minicore.gerbil-matrix.ts.net:11434)
- **RAG:** LlamaIndex + ChromaDB + sentence-transformers
- **Package Manager:** uv
- **Frontend:** Vanilla HTML/JS (no build step)
- **External Services:** Cal.com (webhooks + API), Tailscale Funnel

## Architecture

FastAPI monolith calling Ollama for LLM inference. Flow:

1. Cal.com sends BOOKING_CREATED webhook
2. Server creates intake session, emails chat link to student
3. Student completes 5-8 turn Socratic intake conversation
4. Bot generates structured JSON summary
5. Summary delivered to professor via email and/or Cal.com booking notes

## Conventions

- snake_case for functions/variables, PascalCase for classes
- Pydantic models for all data validation
- ruff for formatting and linting
- pytest for testing
- Conventional commits: `type(scope): message`
- Never commit .env, models/, adapters/, or chroma_db/

## Key Constraints

- All inference runs locally on Mac Mini M4 (no cloud LLM calls)
- Ollama serves Gemma 4 31B (4-bit quantization, ~20GB model)
- Conversations limited to 10 turns max (hard cutoff)
- Student privacy: local-only storage, consent disclosure required
- Chat widget must be mobile-friendly

## Hooks (Mac Mini M4 only)

`.claude/settings.local.json` (gitignored) auto-enables and disables Tailscale
Funnel at session open/close via `SessionStart` and `SessionEnd` hooks:

- `scripts/funnel-on.sh` — enables Funnel (HTTPS :8443) at startup/resume
- `scripts/funnel-off.sh` — disables Funnel at logout/exit (not on /clear)

Both scripts are idempotent. They use `/usr/local/bin/tailscale` (macOS app
CLI v1.94.2) to avoid the Nix CLI version-mismatch warning.

On a new machine: create `~/.local/bin/funnel-on.sh` and `funnel-off.sh` as
thin wrappers (exec the scripts/ versions) and recreate settings.local.json
with the hook config from AGENTS.md or a teammate's copy.

## Known Gotchas

- Ollama must be running before starting the app; /health reports "degraded" if unreachable
- Gemma 4 31B at 4-bit uses ~20GB RAM; on a 32GB workstation with other models loaded, Ollama will evict idle models to make room
- ChromaDB is embedded (no separate process needed)
- Cal.com webhook support depends on plan tier; verify before building integration
- Tailscale Funnel serves on HTTPS :8443 (port 443 is used by Ollama); run `tailscale funnel --bg --https 8443 8000` to expose the dev server
- Public URL: https://mac-minicore.gerbil-matrix.ts.net:8443/
- Hatchling requires `[tool.hatch.build.targets.wheel] packages = ["app"]` in pyproject.toml since the package name doesn't match the source directory
