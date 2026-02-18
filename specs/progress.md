# Application Project Progress

**Project:** Office Hours Intake Bot
**Status:** Phase 0 Complete — Ready for Phase 1
**Last Updated:** 2026-02-17

## Current Status Overview

### Development Phase

- **Current Phase:** Phase 0 complete; Phase 1 (Infrastructure Setup) next
- **Phase Progress:** Phase 0: 100% complete
- **Overall Project Progress:** ~15% complete

### Recent Accomplishments

- Project concept documented in README.md - 2026-02-17
- Project scaffolding and specs created - 2026-02-17
- Intake summary JSON schema finalized (docs/intake-schema.json) - 2026-02-17
- Course taxonomy created for SPA 212-T (rag-corpus/spa212/) - 2026-02-17
- Dialogue flow designed with course and non-course paths (docs/dialogue-flow.md) - 2026-02-17
- System prompt drafted (docs/system-prompt.md) - 2026-02-17

### Active Work

- [ ] Set up Python environment with uv - target: Phase 1
- [ ] Download and benchmark Qwen2.5 3B on Mac Mini M4 - target: Phase 1
- [ ] Stand up baseline FastAPI endpoint - target: Phase 1

## Milestone Tracking

### Completed Milestones

- [x] ~~Project concept and architecture documented~~ - 2026-02-17
- [x] ~~Project scaffolding created~~ - 2026-02-17
- [x] ~~Phase 0 complete (design decisions locked)~~ - 2026-02-17

### Upcoming Milestones

- [ ] Phase 1 complete (baseline model serving) - Target: end of Week 2
- [ ] Phase 2 complete (RAG pipeline working) - Target: end of Week 3
- [ ] Phase 4 complete (fine-tuned model evaluated) - Target: end of Week 5
- [ ] Phase 5 complete (Cal.com integration live) - Target: end of Week 6

### At-Risk Milestones

- None yet

## Build and Test Status

### Build Health

- **Last Successful Build:** N/A (no code yet)

### Test Results

- No tests yet

### Open Defects

- None

## Feature Progress

### Completed Features

- [x] ~~Intake summary JSON schema~~ - 2026-02-17
- [x] ~~Course taxonomy (grammar topics, common errors)~~ - 2026-02-17
- [x] ~~Dialogue flow (course + non-course paths)~~ - 2026-02-17
- [x] ~~System prompt template~~ - 2026-02-17
- [x] ~~Office hours scope and referral resources~~ - 2026-02-17

### In Progress

- None (Phase 1 not started)

### Planned

- [ ] FastAPI baseline endpoint - Phase 1
- [ ] RAG indexing pipeline - Phase 2
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
- **Cloudflare Tunnel:** Free tier should be sufficient

### Pending Updates

- None

## Challenges and Blockers

### Current Blockers

- None

### Resolved Challenges

- None yet

### Lessons Learned

- None yet

## Next Steps

### Immediate Actions (Next 2 Weeks)

- [ ] Set up Python environment with uv and core dependencies
- [ ] Download and benchmark Qwen2.5 3B Instruct on Mac Mini M4
- [ ] Stand up minimal FastAPI /chat endpoint with baseline model
- [ ] Configure Cloudflare Tunnel for external access

### Medium-term Goals (Next Month)

- [ ] RAG pipeline indexing course materials and returning relevant context
- [ ] 10-15 manual test conversations establishing baseline quality
- [ ] Synthetic training data generated and curated

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
