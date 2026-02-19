# Application Project Progress

**Project:** Office Hours Intake Bot
**Status:** Phase 2 In Progress — RAG Pipeline Operational
**Last Updated:** 2026-02-19

## Current Status Overview

### Development Phase

- **Current Phase:** Phase 2 (RAG Pipeline) — core pipeline complete
- **Phase Progress:** Phase 1: ~90% (Tailscale Funnel remaining); Phase 2: ~75% (manual quality testing remaining)
- **Overall Project Progress:** ~35% complete

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

### Active Work

- [ ] Configure Tailscale Funnel for external access - target: Phase 1
- [ ] Benchmark model latency on M4 target hardware - target: Phase 1
- [ ] Test RAG quality with 10-15 manual conversations - target: Phase 2

## Milestone Tracking

### Completed Milestones

- [x] ~~Project concept and architecture documented~~ - 2026-02-17
- [x] ~~Project scaffolding created~~ - 2026-02-17
- [x] ~~Phase 0 complete (design decisions locked)~~ - 2026-02-17
- [x] ~~Python environment and dependencies configured~~ - 2026-02-18
- [x] ~~Base model downloaded and serving via FastAPI~~ - 2026-02-18

### Upcoming Milestones

- [ ] Phase 1 complete (baseline model serving + Funnel) - Target: end of Week 2
- [ ] Phase 2 complete (RAG pipeline + quality validation) - Target: end of Week 3
- [ ] Phase 4 complete (fine-tuned model evaluated) - Target: end of Week 5
- [ ] Phase 5 complete (Cal.com integration live) - Target: end of Week 6

### At-Risk Milestones

- None yet

## Build and Test Status

### Build Health

- **Last Successful Build:** 2026-02-19 (uv sync, all imports verified)

### Test Results

- 9 tests passing (4 original + 5 RAG pipeline tests)
- RAG tests use in-memory ChromaDB with temporary fixtures
- All tests use mocked model calls (no GPU needed for CI)

### Open Defects

- None

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

### In Progress

- [ ] Tailscale Funnel configuration - Phase 1
- [ ] RAG quality validation with manual test conversations - Phase 2

### Planned

- [ ] Intake conversation engine - Phase 2-4
- [ ] Chat widget UI - Phase 5
- [ ] Cal.com webhook integration - Phase 5
- [ ] Summary delivery (email + API) - Phase 5
- [ ] Guardrails and safety checks - Phase 6

### Deferred or Cut

- Pre-booking flow (deferred to v2)
- Multi-language support (deferred to v2)
- Recurring student profiles (deferred to v2)

## Technical Debt

### Known Debt

- None yet

### Recently Resolved

- None

## Dependency Status

### External Dependencies

- **Cal.com:** Webhook support needs verification on current plan
- **MLX-LM:** Requires Apple Silicon (confirmed: Mac Mini M4)
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

## Next Steps

### Immediate Actions (Next 2 Weeks)

- [ ] Configure Tailscale Funnel for external access
- [ ] Benchmark model latency on M4 Mac Mini (confirm <2s target)
- [ ] Test RAG quality with 10-15 manual conversations
- [ ] Begin Phase 3: define student persona matrix for synthetic data

### Medium-term Goals (Next Month)

- [ ] 10-15 manual test conversations establishing baseline quality
- [ ] Synthetic training data generated and curated (300-500 conversations)
- [ ] LoRA fine-tuning with MLX-LM

### Decisions Needed

- Verify Cal.com plan supports webhooks
- Determine acceptable latency threshold (target <2s)
- Decide on chat link expiration policy (e.g., 48 hours post-booking)
- Clarify WFU policy on AI disclosure to students

## Release Planning

### Next Release

- **Version:** v0.1.0 (MVP)
- **Target Date:** End of Week 6
- **Included Features:** Post-booking intake chat, summary delivery, basic guardrails
- **Release Blockers:** Fine-tuned model quality, Cal.com webhook verification

### Release History

| Version | Date | Key Changes |
|---------|------|-------------|
| - | - | No releases yet |
