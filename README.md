# Office Hours Intake Bot

A locally-hosted chatbot that conducts a short intake interview with
visitors who book office hours appointments through Cal.com. The bot
asks a few targeted questions, helps visitors articulate what they need,
and delivers a structured summary to the professor before the meeting.

## The problem

Students often arrive at office hours without a clear sense of what they
need help with. The first several minutes get spent figuring out the
topic, the assignment, and the level of difficulty — time that could be
spent actually working through the problem. Professors, for their part,
have no advance notice of what to prepare.

## What this does

After a visitor books an appointment on Cal.com, they receive a link to
a brief chat conversation (5-8 turns). The bot guides them through
identifying:

- Which course or topic the meeting is about
- The specific area of difficulty (grammar concept, assignment,
  exam prep, etc.)
- How confident they feel about the material
- Any specific assignments or exercises involved

The bot then generates a structured summary and sends it to the
professor ahead of the appointment. The result: visitors arrive having
already reflected on their needs, and the professor can pull up relevant
materials in advance.

Non-course meetings (colleague conversations, advising, committee
check-ins) get a shorter flow — just a brief description of the topic
and any prep requests.

## Approach

The bot runs entirely on a Mac Mini M4 with no cloud LLM dependency.

The stack:

- **LLM inference:** Gemma 4 31B served locally via Ollama
- **Context grounding:** A RAG pipeline (LlamaIndex + ChromaDB) indexes
  course syllabi, grammar topics, assignment descriptions, and common
  student pain points so the bot can ask informed follow-up questions
- **API server:** FastAPI handles the chat sessions, Cal.com webhooks,
  and summary delivery
- **Chat interface:** A minimal HTML/JS widget, mobile-friendly, no
  build tooling
- **Integration:** Cal.com webhooks trigger the intake flow
  post-booking; summaries are delivered via email and/or the Cal.com
  booking API

## Project status

**Phase 0 (Design) — Complete.** Output schema, dialogue flow, course
taxonomy, and system prompt are finalized in `docs/` and `rag-corpus/`.

**Phase 1 (Infrastructure) — Complete.** FastAPI app with /health and
/chat endpoints, Tailscale Funnel for external HTTPS access, test suite
(18 tests passing).

**Phase 2 (RAG Pipeline) — In progress.** LlamaIndex + ChromaDB
pipeline built and wired into /chat. Remaining: quality validation with
manual test conversations using Gemma 4.

**Phases 3-4 (Fine-tuning) — Deferred.** Switched from Qwen 2.5 3B +
LoRA fine-tuning to Gemma 4 31B with prompt engineering + RAG. Will
revisit fine-tuning after collecting real conversation data.

See `specs/` for detailed planning, progress tracking, and
implementation notes.

## License

TBD
