# Application Project Planning

**Project:** Office Hours Intake Bot
**Status:** Planning
**Last Updated:** 2026-02-17

## Project Overview

### Software Description

- **Application Type:** Web application (FastAPI backend + chat widget frontend)
- **Target Platform:** macOS (Mac Mini M4), accessed via Cloudflare Tunnel
- **Primary Language:** Python 3.11+
- **Key Libraries/Frameworks:** FastAPI, MLX-LM, LlamaIndex, ChromaDB, sentence-transformers, uv

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

- **Pattern:** Monolith (single FastAPI service with embedded LLM inference)
- **Data Flow:** Cal.com webhook -> FastAPI -> intake chat session -> summary generation -> email/Cal.com API delivery
- **Key Components:**
  - Intake Bot: fine-tuned LLM served via MLX-LM
  - RAG Pipeline: LlamaIndex + ChromaDB indexing course materials
  - Chat Widget: vanilla HTML/JS frontend served by FastAPI
  - Summary Delivery: email and/or Cal.com booking notes update

### External Dependencies

- **APIs and Services:** Cal.com (webhooks, booking API), Cloudflare Tunnel
- **Data Sources:** Course syllabi, assignment descriptions, grammar topics, common error patterns (local files)
- **Build Tools:** uv (package management), MLX-LM (model conversion and fine-tuning)

### Technical Constraints

- Latency target: <2s per LLM turn on Mac Mini M4
- 3B parameter model preferred for speed; 7B fallback if quality is insufficient
- Local-only data storage (privacy requirement)
- Mobile-friendly chat UI (students will use phones)

## Timeline and Milestones

### Phase 0: Scoping and Design (Week 1)

- [ ] Lock integration point decision (post-booking confirmed)
- [ ] Finalize output JSON schema
- [ ] Define course taxonomy (topics, pain points, assignments)
- [ ] Sketch dialogue flow (5-8 turn pattern)

### Phase 1: Infrastructure Setup (Weeks 1-2)

- [ ] Set up Python environment with uv
- [ ] Download and benchmark base model (Qwen2.5 3B Instruct)
- [ ] Stand up minimal FastAPI endpoint with baseline model
- [ ] Configure Cloudflare Tunnel for external access

### Phase 2: RAG Pipeline (Weeks 2-3)

- [ ] Organize course document corpus
- [ ] Build LlamaIndex + ChromaDB indexing pipeline
- [ ] Implement RAG-augmented prompt construction
- [ ] Test RAG quality with 10-15 manual conversations

### Phase 3: Training Data Generation (Weeks 3-4)

- [ ] Define student persona matrix
- [ ] Generate 300-500 synthetic intake conversations via frontier model
- [ ] Curate and edit generated conversations
- [ ] Prepare train/val/test splits in MLX JSONL format

### Phase 4: Fine-Tuning with LoRA (Weeks 4-5)

- [ ] Configure and run LoRA fine-tuning via MLX-LM
- [ ] Monitor training metrics and spot-check quality
- [ ] Fuse adapter into deployable model
- [ ] Evaluate against held-out test set (target avg score >= 2.5/3)

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
- MLX and MLX-LM (Apple Silicon native)
- Mac Mini M4 (development and production host)
- direnv + flake.nix for reproducible environment

### Infrastructure

- Mac Mini M4 as local server
- Cloudflare Tunnel for HTTPS access
- Cal.com (existing booking platform)
- Email service for summary delivery

### Collaboration

- Solo developer (professor/owner)
- Git-based version control
- Claude Code for AI-assisted development

## Risk Assessment

### Technical Risks

- Model quality insufficient at 3B params: benchmark against 7B, upgrade if needed
- Cloudflare tunnel instability: add health check + auto-restart
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

- [ ] Latency < 2s per turn on Mac Mini M4
- [ ] Student abandonment rate < 20%
- [ ] Professor finds summaries useful in >= 80% of sessions

### Adoption Criteria

- [ ] Bot deployed and accessible via Cal.com post-booking flow
- [ ] Students receive chat link automatically after booking
- [ ] Feedback mechanism (thumbs up/down) in place
