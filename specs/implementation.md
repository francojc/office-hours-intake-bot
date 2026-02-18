# Application Implementation Details

**Project:** Office Hours Intake Bot
**Status:** Planning
**Last Updated:** 2026-02-17

## Architecture

### System Design

- **Architecture Pattern:** Monolith (FastAPI service with embedded LLM)
- **Primary Language:** Python 3.11+
- **Framework:** FastAPI + Uvicorn
- **Build System:** uv (package manager and virtual environment)

### Component Overview

```
office-hours-intake-bot/
├── app/                   # Application source code
│   ├── main.py            # FastAPI entry point
│   ├── chat.py            # Intake conversation engine
│   ├── rag.py             # RAG pipeline (LlamaIndex + ChromaDB)
│   ├── summary.py         # Summary generation and schema validation
│   ├── delivery.py        # Email and Cal.com API delivery
│   ├── webhooks.py        # Cal.com webhook handlers
│   └── config.py          # Configuration and environment handling
├── models/                # Downloaded/fused LLM models
│   └── qwen2.5-3b/        # Base model (MLX format)
├── adapters/              # LoRA adapter checkpoints
│   └── intake-bot-v1/     # Fine-tuned adapter weights
├── rag-corpus/            # Source documents for RAG indexing
│   ├── spa212/            # SPA 212-T course materials
│   └── general/           # Office hours scope, referral resources
├── chroma_db/             # ChromaDB persistent vector store
├── training-data/         # Fine-tuning data (JSONL)
│   ├── train.jsonl
│   ├── val.jsonl
│   └── test.jsonl
├── static/                # Chat widget frontend assets
│   ├── index.html
│   ├── style.css
│   └── chat.js
├── tests/                 # Test suite
│   ├── test_chat.py
│   ├── test_rag.py
│   ├── test_summary.py
│   └── test_webhooks.py
├── logs/                  # Weekly reviews and session logs
├── specs/                 # Project planning and tracking
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock               # Locked dependency versions
└── flake.nix             # Nix development environment
```

### Key Modules

1. **app/chat.py — Intake Conversation Engine**
   - **Purpose:** Manages multi-turn intake dialogue with students
   - **Public Interface:** `IntakeSession` class, `process_turn()`, `is_complete()`
   - **Dependencies:** MLX-LM (model inference), RAG pipeline (context retrieval)

2. **app/rag.py — RAG Pipeline**
   - **Purpose:** Indexes course materials and retrieves relevant context per conversation turn
   - **Public Interface:** `build_index()`, `retrieve_context(query)`
   - **Dependencies:** LlamaIndex, ChromaDB, sentence-transformers

3. **app/webhooks.py — Cal.com Integration**
   - **Purpose:** Handles incoming webhooks (https://cal.com/docs/developing/guides/automation/webhooks) and outgoing API calls to Cal.com
   - **Public Interface:** `booking_confirmed()` endpoint, `update_booking_notes()`
   - **Dependencies:** httpx, Cal.com API (https://cal.com/docs/api-reference/v2/)

4. **app/summary.py — Summary Generation**
   - **Purpose:** Validates and formats the structured intake summary
   - **Public Interface:** `IntakeSummary` (Pydantic model), `generate_summary()`
   - **Dependencies:** Pydantic

5. **app/delivery.py — Summary Delivery**
   - **Purpose:** Sends completed summaries via email and/or Cal.com API
   - **Public Interface:** `deliver_summary()`
   - **Dependencies:** httpx, email libraries

### Data Model

- **Primary Data Structures:** `IntakeSummary` (Pydantic), `ChatSession` (in-memory dict keyed by session_id)
- **Persistence Layer:** ChromaDB for vector store; conversation logs stored as local JSON files
- **Serialization Format:** JSON for summaries and API payloads
- **Migration Strategy:** Schema changes handled via Pydantic model versioning

## Development Environment

### Setup

- **Language Runtime:** Python 3.11+ (via uv)
- **Package Manager:** uv with uv.lock for reproducibility
- **Environment Management:** uv venv + direnv + flake.nix
- **Local Services:** ChromaDB (embedded, no separate process)

### Build and Run

```bash
# Install dependencies
uv sync

# Run locally (development)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run in production
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Expose via Cloudflare Tunnel
cloudflared tunnel --url http://localhost:8000
```

### Model Operations

```bash
# Download and convert base model
uv run mlx_lm.convert --hf-path Qwen/Qwen2.5-3B-Instruct --mlx-path ./models/qwen2.5-3b

# Fine-tune with LoRA
uv run mlx_lm.lora \
  --model ./models/qwen2.5-3b \
  --train --data ./training-data/ \
  --batch-size 4 --lora-layers 8 --iters 1000 \
  --adapter-path ./adapters/intake-bot-v1

# Fuse adapter into model
uv run mlx_lm.fuse \
  --model ./models/qwen2.5-3b \
  --adapter-path ./adapters/intake-bot-v1 \
  --save-path ./models/intake-bot-v1-fused
```

### Code Standards

- **Formatting:** ruff format
- **Linting:** ruff check
- **Type Checking:** Pydantic for runtime validation; mypy optional
- **Naming Conventions:** snake_case for functions/variables, PascalCase for classes

## Testing Strategy

### Test Levels

- **Unit Tests:** pytest, in tests/ directory, test_*.py naming
- **Integration Tests:** pytest with FastAPI TestClient
- **End-to-End Tests:** Manual testing against live model (quality evaluation rubric)

### Running Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest tests/test_summary.py tests/test_rag.py

# With coverage
uv run pytest --cov=app
```

### Coverage Targets

- **Overall:** 70%+ for application logic (excludes model inference)
- **Critical Paths:** Summary schema validation, webhook handling
- **Exclusions:** LLM inference quality (tested via evaluation rubric, not unit tests)

### Test Data

- **Fixtures:** tests/fixtures/ with sample conversations and webhook payloads
- **Mocks:** Mock MLX-LM model responses for unit tests
- **Test Databases:** In-memory ChromaDB for RAG tests

## Deployment

### Target Environment

- **Platform:** Mac Mini M4 (local server)
- **Runtime:** Python process managed by systemd/launchd
- **Configuration:** .env file for secrets (Cal.com API key, email credentials)

### Release Process

- **Versioning:** SemVer
- **Release Steps:** Tag, test on Mac Mini, restart service
- **Rollback Procedure:** Revert to previous model and code via git

## Monitoring and Observability

### Logging

- **Framework:** Python logging (structured JSON to file)
- **Log Levels:** INFO for conversation events, WARNING for guardrail triggers, ERROR for failures

### Error Handling

- **User-Facing Errors:** Friendly messages in chat widget; never expose stack traces
- **Error Reporting:** Log to local file; review weekly

### Health Checks

- **Endpoints:** GET /health returns model status and uptime
- **Dependency Checks:** ChromaDB collection count, model loaded flag

## Security Considerations

### Input Validation

- **User Input:** Pydantic validation on all API payloads; sanitize chat input
- **API Boundaries:** Webhook signature verification for Cal.com
- **File Handling:** RAG corpus is read-only; no user file uploads

### Authentication and Authorization

- **Auth Method:** Session ID in URL (no login required for students)
- **Permission Model:** None (single-user system, professor is sole admin)
- **Secret Management:** .env file, never committed to git

### Privacy

- All data stored locally on Mac Mini (no cloud)
- Consent disclosure at start of every chat session
- Retention policy: conversation logs deleted after 90 days

## Decision Log

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| 2026-02-17 | Post-booking integration point | Simpler; student already committed | Pre-booking (more ambitious, deferred to v2) |
| 2026-02-17 | Qwen2.5 3B Instruct as base model | Multilingual (Spanish context), fast on M4 | Llama 3.2 3B, Mistral 7B |
| 2026-02-17 | uv for package management | Fast, lockfile-based, replaces pip/venv/poetry | pip+venv, poetry, conda |
| 2026-02-17 | ChromaDB for vector store | Embedded, no separate process, persistent | LanceDB, Pinecone (cloud) |
| 2026-02-17 | Vanilla HTML/JS for chat UI | No build tooling, simple to maintain | React, Vue |
| 2026-02-17 | 4-level self-assessment scale | More descriptive than low/medium/high; maps to actionable prep | Numeric 1-5 scale, free-text |
| 2026-02-17 | Conversation log stored separately from summary | Summary is the delivery artifact; logs kept locally for privacy | Embedding full transcript in summary JSON |
| 2026-02-17 | Non-course flow for colleagues | 3-4 turn lightweight path; avoids forcing non-students through course taxonomy | Single flow for all visitors |
| 2026-02-17 | Snake_case subcategory vocabulary | Consistent labels for fine-tuning and analysis; model picks from fixed list | Free-text subcategories |
