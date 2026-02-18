# Office Hours Intake Bot

> This project is under active development. The design phase is
> complete; implementation has not yet begun.

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

- **LLM inference:** A fine-tuned 3B parameter model (Qwen2.5 Instruct)
  served via MLX, Apple's native machine learning framework for Silicon
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

Fine-tuning data will be generated synthetically from a persona matrix
covering different courses, difficulty levels, communication styles, and
issue types, then curated by hand before training.

## Project status

**Phase 0 (Design) — Complete.** Output schema, dialogue flow, course
taxonomy, and system prompt are finalized in `docs/` and `rag-corpus/`.

**Phase 1 (Infrastructure) — Not started.** Next steps: initialize the
Python environment, download the base model, stand up a baseline API
endpoint.

See `specs/` for detailed planning, progress tracking, and
implementation notes.

## License

TBD
