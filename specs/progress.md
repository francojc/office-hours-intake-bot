# Application Project Progress

**Project:** Office Hours Intake Bot
**Status:** Planning
**Last Updated:** 2026-02-17

## Current Status Overview

### Development Phase

- **Current Phase:** Architecture & Design (Phase 0)
- **Phase Progress:** 0% complete
- **Overall Project Progress:** 0% complete

### Recent Accomplishments

- Project concept documented in README.md - 2026-02-17
- Project scaffolding and specs created - 2026-02-17

### Active Work

- [ ] Finalize output JSON schema - target: Week 1
- [ ] Define course taxonomy for SPA 212-T - target: Week 1
- [ ] Sketch dialogue flowchart - target: Week 1

## Milestone Tracking

### Completed Milestones

- [x] ~~Project concept and architecture documented~~ - 2026-02-17
- [x] ~~Project scaffolding created~~ - 2026-02-17

### Upcoming Milestones

- [ ] Phase 0 complete (design decisions locked) - Target: end of Week 1
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

- None yet

### In Progress

- [ ] Output JSON schema design - 0% complete

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

- [ ] Finalize output JSON schema based on real booking patterns
- [ ] Document course taxonomy for SPA 212-T
- [ ] Set up Python environment with uv and core dependencies
- [ ] Download and benchmark Qwen2.5 3B Instruct on Mac Mini M4

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
