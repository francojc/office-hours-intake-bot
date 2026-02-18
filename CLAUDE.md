# Office Hours Intake Bot

AI-powered student intake chatbot for Cal.com office hours appointments.
Runs locally on Mac Mini M4 with a fine-tuned LLM via MLX.

## Quick Reference

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Lint and format
uv run ruff check app/ tests/
uv run ruff format app/ tests/

# Download base model
uv run mlx_lm.convert --hf-path Qwen/Qwen2.5-3B-Instruct --mlx-path ./models/qwen2.5-3b

# Fine-tune with LoRA
uv run mlx_lm.lora --model ./models/qwen2.5-3b --train --data ./training-data/ --adapter-path ./adapters/intake-bot-v1

# Expose via Tailscale Funnel
tailscale funnel 8000
```

## Project Structure

```
office-hours-intake-bot/
├── app/                   # FastAPI application source
│   ├── main.py            # Entry point and route mounting
│   ├── chat.py            # Multi-turn intake conversation engine
│   ├── rag.py             # LlamaIndex + ChromaDB RAG pipeline
│   ├── summary.py         # Pydantic models for intake summary schema
│   ├── delivery.py        # Email and Cal.com API summary delivery
│   ├── webhooks.py        # Cal.com webhook handlers
│   └── config.py          # Settings and environment variables
├── models/                # MLX-format LLM models (gitignored)
├── adapters/              # LoRA adapter checkpoints (gitignored)
├── rag-corpus/            # Course materials for RAG indexing
│   ├── spa212/            # SPA 212-T syllabus, assignments, topics
│   └── general/           # Office hours scope, referral resources
├── chroma_db/             # ChromaDB persistent store (gitignored)
├── training-data/         # Fine-tuning JSONL files
├── static/                # Chat widget HTML/CSS/JS
├── tests/                 # pytest test suite
├── specs/                 # Planning, progress, implementation docs
├── logs/                  # Weekly reviews and session logs
├── pyproject.toml         # Dependencies and project metadata
└── uv.lock               # Locked dependency versions
```

## Tech Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI + Uvicorn
- **LLM:** Qwen2.5 3B Instruct via MLX-LM (Apple Silicon native)
- **RAG:** LlamaIndex + ChromaDB + sentence-transformers
- **Package Manager:** uv
- **Frontend:** Vanilla HTML/JS (no build step)
- **External Services:** Cal.com (webhooks + API), Tailscale Funnel

## Architecture

FastAPI monolith with embedded LLM inference. Flow:

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
- Target latency: <2s per conversation turn
- Conversations limited to 10 turns max (hard cutoff)
- Student privacy: local-only storage, consent disclosure required
- Chat widget must be mobile-friendly

## Known Gotchas

- MLX-LM requires Apple Silicon; will not work on Intel Macs
- ChromaDB is embedded (no separate process needed)
- Cal.com webhook support depends on plan tier; verify before building integration
- Tailscale Funnel must be enabled on the tailnet; run `tailscale funnel 8000` to expose the dev server
