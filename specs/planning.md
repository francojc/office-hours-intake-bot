# Application Project Planning

**Project:** Office Hours Intake Bot
**Status:** Phase 2 In Progress (model switched to Ollama/Gemma 4)
**Last Updated:** 2026-04-09

## Project Overview

### Software Description

- **Application Type:** Web application (FastAPI backend + chat widget frontend)
- **Target Platform:** macOS (Mac Mini M4), accessed via Tailscale Funnel
- **Primary Language:** Python 3.11+
- **Key Libraries/Frameworks:** FastAPI, Ollama (Gemma 4 31B), LlamaIndex, ChromaDB, sentence-transformers, uv

### Problem Statement

- Students arrive at office hours without having articulated what they need help with, leading to less productive sessions.
- Professors lack advance notice of the topic or difficulty level, so they cannot prepare relevant materials.
- No existing Cal.com feature provides a structured, AI-guided intake interview tied to booking.

### Goals and Non-Goals

#### Goals

- [ ] Guide students through a 5-8 turn Socratic intake conversation post-booking
- [ ] Produce a structured JSON summary delivered to the professor before the appointment
- [ ] Run entirely on a Mac Mini M4 with no cloud LLM dependency
- [ ] Integrate with Cal.com via webhooks and booking metadata API

#### Non-Goals

- Pre-booking flow (v2 feature)
- Multi-language conversation support (v2)
- Recurring student profiles or cross-session tracking (v2)
- Replacing office hours themselves

## Architecture and Design

### High-Level Architecture

- **Pattern:** Monolith (FastAPI service calling Ollama for LLM inference)
- **Data Flow:** Cal.com webhook -> FastAPI -> intake chat session -> summary generation -> email/Cal.com API delivery
- **Key Components:**
  - Intake Bot: Gemma 4 31B served via Ollama
  - RAG Pipeline: LlamaIndex + ChromaDB indexing course materials
  - Chat Widget: vanilla HTML/JS frontend served by FastAPI
  - Summary Delivery: email and/or Cal.com booking notes update

### External Dependencies

- **APIs and Services:** Cal.com (webhooks, booking API), Tailscale Funnel, Ollama (LLM inference)
- **Data Sources:** Course syllabi, assignment descriptions, grammar topics, common error patterns (local files)
- **Build Tools:** uv (package management)

### Technical Constraints

- Gemma 4 31B (4-bit) via Ollama; latency TBD (original <2s target not achievable)
- 32GB Mac Mini M4 with other workloads; Ollama manages model eviction
- Local-only data storage (privacy requirement)
- Mobile-friendly chat UI (students will use phones)

## Timeline and Milestones

### Phase 0: Scoping and Design (Week 1) -- COMPLETE

- [x] Lock integration point decision (post-booking confirmed)
- [x] Finalize output JSON schema (docs/intake-schema.json)
- [x] Define course taxonomy (rag-corpus/spa212/)
- [x] Sketch dialogue flow (docs/dialogue-flow.md)
- [x] Draft system prompt (docs/system-prompt.md)
- [x] Add non-course meeting flow for colleagues/non-course visitors

### Phase 1: Infrastructure Setup (Weeks 1-2) -- COMPLETE

- [x] Set up Python environment with uv (158 packages, pyproject.toml)
- [x] Download and benchmark base model (Qwen2.5 3B Instruct, bfloat16)
- [x] Stand up minimal FastAPI endpoint with baseline model (/health, /chat)
- [x] Configure Tailscale Funnel for external access (HTTPS :8443 → localhost:8000)
- [x] Initial test suite (4 tests passing)
- [x] M4 latency benchmark: warm avg ~8.8s per turn (original <2s target needs revision)

### Phase 2: RAG Pipeline (Weeks 2-3) -- IN PROGRESS

- [x] Organize course document corpus
- [x] Build LlamaIndex + ChromaDB indexing pipeline
- [x] Implement RAG-augmented prompt construction
- [ ] Test RAG quality with 10-15 manual conversations

### Phase 3: Training Data Generation (Weeks 3-4) -- DEFERRED

Deferred: switching to Gemma 4 31B via Ollama with prompt engineering + RAG
instead of fine-tuning. Will revisit fine-tuning in v1.1 after collecting
real conversation data.

- [x] Define student persona matrix (32 personas)
- [x] Build synthetic data generator
- [ ] ~~Generate 300-500 synthetic conversations~~ (deferred)
- [ ] ~~Prepare train/val/test splits~~ (deferred)

### Phase 4: Fine-Tuning with LoRA (Weeks 4-5) -- DEFERRED

Deferred: relying on Gemma 4 31B base capabilities for MVP.

- [ ] ~~Configure and run LoRA fine-tuning~~ (deferred)
- [ ] ~~Fuse adapter into deployable model~~ (deferred)
- [ ] ~~Evaluate against held-out test set~~ (deferred)

### Phase 5: Cal.com Integration (Weeks 5-6)

- [ ] Set up Cal.com webhook for BOOKING_CREATED events
- [ ] Implement booking confirmation flow and session management
- [ ] Build mobile-friendly chat widget UI
- [ ] Implement summary delivery (email + Cal.com booking notes)

### Phase 6: Hardening and Iteration (Ongoing)

- [ ] Add conversation logging with student consent disclosure
- [ ] Implement guardrails (distress detection, off-topic redirect, turn limit)
- [ ] Define privacy policy and data retention schedule
- [ ] Collect feedback and iterate on fine-tuning

## Resources and Requirements

### Development Environment

- Python 3.11+ via uv
- Ollama for LLM inference (Gemma 4 31B)
- Mac Mini M4 (development and production host)
- direnv + flake.nix for reproducible environment

### Infrastructure

- Mac Mini M4 as local server
- Tailscale Funnel for HTTPS access
- Cal.com (existing booking platform)
- Email service for summary delivery

### Collaboration

- Solo developer (professor/owner)
- Git-based version control
- Claude Code for AI-assisted development

## Risk Assessment

### Technical Risks

- Model quality insufficient at 31B 4-bit: fallback to smaller quantization-aware model
- Tailscale Funnel instability: add health check + auto-restart
- M4 thermal throttling under load: unlikely with single-user sequential load

### Scope Risks

- Feature creep toward pre-booking flow or multi-language: defer to v2
- Fine-tuning data not diverse enough: ensure persona matrix coverage
- Cal.com plan may not support webhooks: verify before building integration

## Success Metrics

### Functional Criteria

- [ ] Intake conversations resolve in <= 8 turns
- [ ] JSON summaries are well-formed and match schema
- [ ] issue_description accurately reflects the student's problem
- [ ] professor_prep_note provides actionable context

### Quality Criteria

- [ ] Latency acceptable for async intake chat (target TBD, original <2s not achievable)
- [ ] Student abandonment rate < 20%
- [ ] Professor finds summaries useful in >= 80% of sessions

### Adoption Criteria

- [ ] Bot deployed and accessible via Cal.com post-booking flow
- [ ] Students receive chat link automatically after booking
- [ ] Feedback mechanism (thumbs up/down) in place
