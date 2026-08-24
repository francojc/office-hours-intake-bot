# Application Project Progress

**Project:** Office Hours Intake Bot
**Status:** Phase 2 In Progress — Model switched to Ollama/Gemma 4
**Last Updated:** 2026-08-24

## Current Status Overview

### Development Phase

- **Current Phase:** Phase 2 (RAG quality validation with new model)
- **Phase Progress:** Phase 1: COMPLETE; Phase 2: ~75% (manual quality testing remaining); Phase 3-4: DEFERRED (skipping fine-tuning for MVP)
- **Overall Project Progress:** ~40% complete (adjusted for model switch)

### Recent Accomplishments

- Project concept documented in README.md - 2026-02-17
- Project scaffolding and specs created - 2026-02-17
- Intake summary JSON schema finalized (docs/intake-schema.json) - 2026-02-17
- Course taxonomy created for SPA 212-T (rag-corpus/spa212/) - 2026-02-17
- Dialogue flow designed with course and non-course paths (docs/dialogue-flow.md) - 2026-02-17
- System prompt drafted (docs/system-prompt.md) - 2026-02-17
- Python environment set up with uv (158 packages) - 2026-02-18
- Qwen2.5 3B Instruct downloaded and converted to MLX bfloat16 - 2026-02-18
- FastAPI skeleton with /health and /chat endpoints - 2026-02-18
- Initial test suite (4 tests passing) - 2026-02-18
- Switched from Cloudflare Tunnel to Tailscale Funnel - 2026-02-18
- RAG pipeline built: LlamaIndex + ChromaDB + all-MiniLM-L6-v2 embeddings - 2026-02-19
- System prompt template loaded from docs/system-prompt.md with {{retrieved_context}} injection - 2026-02-19
- RAG context wired into /chat endpoint (replaces hardcoded system message) - 2026-02-19
- Startup lifespan handler indexes corpus automatically (4 docs) - 2026-02-19
- /health endpoint now reports rag_index_loaded status - 2026-02-19
- Test suite expanded to 9 tests (5 new RAG tests) - 2026-02-19
- Added llama-index-embeddings-huggingface dependency - 2026-02-19
- IntakeSummary Pydantic model created (app/summary.py) with full enum constraints - 2026-02-28
- Added pytest-cov to dev dependencies; coverage baseline measured at 90% - 2026-02-28
- Student persona matrix defined (32 personas covering all dialogue paths) - 2026-02-28
- Synthetic training data generator built (scripts/generate_training_data.py) - 2026-02-28
- Initial training data generated: 128 train, 16 val, 16 test conversations - 2026-02-28
- Summary test suite added (9 tests for validation, enums, serialization) - 2026-02-28
- Test suite expanded to 18 tests total (9 app/RAG + 9 summary) - 2026-02-28
- Tailscale Funnel configured on HTTPS port 8443 → localhost:8000 - 2026-02-28
- M4 latency benchmarked: cold start ~10s, warm avg ~8.8s (6.8-12.3s range) - 2026-02-28
- Phase 1 complete - 2026-02-28
- Switched from MLX-LM/Qwen 2.5 3B to Ollama/Gemma 4 31B - 2026-04-09
- Removed mlx-lm dependency, chat.py now uses httpx → Ollama API - 2026-04-09
- Deferred Phases 3-4 (fine-tuning): using Gemma 4 base with prompt engineering + RAG for MVP - 2026-04-09
- Project resumed after 137-day gap; repo review and docs refresh - 2026-08-24
- Verified environment reproducibility (fresh uv sync) and test suite health: 17/18 pass, 1 flaky RAG test - 2026-08-24
- Renamed CLAUDE.md to AGENTS.md; refreshed README development section - 2026-08-24
- Vetted Cal.com integration: free-tier BOOKING_CREATED webhook + /v2 API confirmed; dropped booking-notes delivery (v2 can't patch notes on existing booking), summary goes by email; decision to stay on Cal.com SaaS for MVP - 2026-08-24

### Active Work

- [x] ~~Configure Tailscale Funnel for external access~~ - Phase 1, done 2026-02-28
- [x] ~~Benchmark model latency on M4 target hardware~~ - Phase 1, done 2026-02-28
- [x] ~~Switch from MLX-LM/Qwen 2.5 3B to Ollama/Gemma 4 31B~~ - 2026-04-09
- [ ] Test RAG quality with 10-15 manual conversations using Gemma 4 - target: Phase 2
- [ ] Vetting Cal.com integration (webhook ✓ verified free tier, booking-notes ✗ unsupported, provider adapter) - Phase 5
- [ ] ~~Curate and expand synthetic training data~~ (deferred — skipping fine-tuning for MVP)
- [ ] ~~Review generated conversations~~ (deferred)

## Milestone Tracking

### Completed Milestones

- [x] ~~Project concept and architecture documented~~ - 2026-02-17
- [x] ~~Project scaffolding created~~ - 2026-02-17
- [x] ~~Phase 0 complete (design decisions locked)~~ - 2026-02-17
- [x] ~~Python environment and dependencies configured~~ - 2026-02-18
- [x] ~~Base model downloaded and serving via FastAPI~~ - 2026-02-18
- [x] ~~IntakeSummary Pydantic model implemented~~ - 2026-02-28
- [x] ~~Student persona matrix defined (32 personas)~~ - 2026-02-28
- [x] ~~Synthetic training data generator built~~ - 2026-02-28
- [x] ~~Tailscale Funnel configured (HTTPS :8443)~~ - 2026-02-28
- [x] ~~M4 latency benchmarked~~ - 2026-02-28

### Upcoming Milestones

- [x] ~~Phase 1 complete (baseline model serving + Funnel)~~ - 2026-02-28
- [x] ~~Model switch to Ollama/Gemma 4 31B~~ - 2026-04-09
- [ ] Phase 2 complete (RAG quality validation with Gemma 4)
- [ ] Phase 5 (Cal.com integration — webhook, chat widget, summary delivery)
- [ ] Phase 6 (Hardening — guardrails, logging, privacy policy)

### At-Risk Milestones

- Original Week 6 MVP target has passed; timeline needs resetting after 37-day gap

## Build and Test Status

### Build Health

- **Last Successful Build:** 2026-04-09 (uv sync, all tests passing after Ollama switch)

### Test Results

- 18 tests passing (4 app/main + 5 RAG + 9 summary)
- Chat tests mock httpx calls to Ollama (no live model needed)
- RAG tests use in-memory ChromaDB with temporary fixtures

### Open Defects

- Flaky test: `tests/test_rag.py::test_build_index_creates_collection` fails intermittently in full-suite runs (ChromaDB OSError), passes in isolation. Suspected tmp-dir/HF-download race; needs investigation

## Feature Progress

### Completed Features

- [x] ~~Intake summary JSON schema~~ - 2026-02-17
- [x] ~~Course taxonomy (grammar topics, common errors)~~ - 2026-02-17
- [x] ~~Dialogue flow (course + non-course paths)~~ - 2026-02-17
- [x] ~~System prompt template~~ - 2026-02-17
- [x] ~~Office hours scope and referral resources~~ - 2026-02-17
- [x] ~~RAG indexing pipeline (LlamaIndex + ChromaDB)~~ - 2026-02-19
- [x] ~~RAG-augmented prompt construction in /chat~~ - 2026-02-19
- [x] ~~System prompt template loading from file~~ - 2026-02-19
- [x] ~~IntakeSummary Pydantic model (app/summary.py)~~ - 2026-02-28
- [x] ~~Student persona matrix (32 personas)~~ - 2026-02-28
- [x] ~~Synthetic training data generator~~ - 2026-02-28
- [x] ~~Initial training data (160 conversations: 128/16/16 split)~~ - 2026-02-28
- [x] ~~Tailscale Funnel (HTTPS :8443 → localhost:8000)~~ - 2026-02-28

### In Progress

- [ ] RAG quality validation with manual test conversations using Gemma 4 - Phase 2

### Planned

- [ ] Multi-turn conversation engine with session state - Phase 2/5
- [ ] Chat widget UI - Phase 5
- [ ] Cal.com webhook integration - Phase 5
- [ ] Summary delivery (email + API) - Phase 5
- [ ] Guardrails and safety checks - Phase 6

### Deferred or Cut

- LoRA fine-tuning (deferred — using Gemma 4 base + prompt engineering for MVP)
- Training data curation and expansion (deferred until real data available)
- Pre-booking flow (deferred to v2)
- Multi-language support (deferred to v2)
- Recurring student profiles (deferred to v2)

## Technical Debt

### Known Debt

- Dev dependencies defined in `[project.optional-dependencies]` instead of `[dependency-groups]`; plain `uv sync` does not install pytest/ruff. Consider migrating

### Recently Resolved

- None

## Dependency Status

### External Dependencies

- **Cal.com:** Webhook support VERIFIED on free plan (2026-08-24): BOOKING_CREATED trigger + /v2 API key auth (120 req/min). Public HTTPS subscriber URL required — satisfied by Tailscale Funnel :8443. No endpoint to patch booking notes on existing booking. Provider sits behind thin adapter (see decision log in implementation.md).
- **Ollama:** Running on Mac Mini M4 (http://mac-minicore.gerbil-matrix.ts.net:11434)
- **Tailscale Funnel:** Already available on the tailnet

### Pending Updates

- None

## Challenges and Blockers

### Current Blockers

- None

### Resolved Challenges

- Hatchling build backend config required explicit `packages = ["app"]` in pyproject.toml

### Lessons Learned

- MLX inference on M3 (~3.4 tok/s for 3B model) is much slower than M4 target; benchmark on target hardware before tuning model size
- Lazy model loading in the chat endpoint lets the app start and serve /health even before the model is downloaded
- M4 latency benchmark (Qwen2.5 3B, bfloat16): cold start ~10s, warm avg ~8.8s (range 6.8-12.3s). The <2s target is not achievable with the current ~5K-char system prompt (~1,258 tokens prefill) plus up to 256 generation tokens
- Tailscale Funnel adds negligible latency (~0.1s overhead vs localhost)
- Switching from embedded MLX-LM to Ollama HTTP API simplified chat.py significantly — removed model state management, let Ollama handle lifecycle and quantization
- A stronger base model (31B vs 3B) makes the skip-fine-tuning strategy viable; prompt engineering + RAG can carry the MVP

## Next Steps

### Immediate Actions (Next 2 Weeks)

- [ ] Fix flaky `test_build_index_creates_collection` RAG test
- [ ] Migrate dev deps from `[project.optional-dependencies]` to `[dependency-groups]`
- [ ] Benchmark Gemma 4 31B latency on M4 via Ollama (replaces old Qwen benchmark)
- [ ] Test RAG quality with 10-15 manual conversations using Gemma 4
- [ ] Verify Cal.com plan supports webhooks (biggest external risk)
- [ ] Decide on acceptable latency threshold for async intake chat

### Medium-term Goals (Next Month)

- [ ] Build multi-turn conversation engine with session state management
- [ ] Implement Cal.com BOOKING_CREATED webhook handler
- [ ] Build mobile-friendly chat widget UI
- [ ] Implement summary delivery (email + Cal.com booking notes)

### Decisions Needed

- ~~Verify Cal.com plan supports webhooks~~ (resolved 2026-08-24: free tier supports webhooks + API; summary delivery email-only)
- Determine acceptable latency threshold (Gemma 4 31B on M4 via Ollama)
- Decide on chat link expiration policy (e.g., 48 hours post-booking)
- Clarify WFU policy on AI disclosure to students

## Release Planning

### Next Release

- **Version:** v0.1.0 (MVP)
- **Target Date:** TBD (original Week 6 target passed; reset after resuming)
- **Included Features:** Post-booking intake chat, summary delivery, basic guardrails
- **Release Blockers:** Cal.com webhook verification, conversation engine, chat widget

### Release History

| Version | Date | Key Changes |
|---------|------|-------------|
| - | - | No releases yet |
