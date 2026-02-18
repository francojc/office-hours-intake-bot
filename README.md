# Office Hours Intake Chatbot

## AI-Powered Student Appointment Intake for Cal.com

**Project:** Office Hours Intake Bot
**Owner:** [Your Name] — Wake Forest University
**Last Updated:** 2026-02-17
**Status:** Planning

---

## Project Overview

Build a locally-hosted, fine-tuned LLM chatbot that integrates with Cal.com to conduct a structured intake interview with students before (or immediately after) booking an office hours appointment. The bot guides students toward metacognitive clarity about their needs and produces a structured summary delivered to the professor pre-session.

### Core Goals

1. Help students articulate *what* they need help with before arriving
2. Deliver a structured pre-session brief to the professor
3. Run entirely on a Mac Mini M4 (local, private, no cloud dependency)
4. Integrate cleanly into the existing Cal.com booking workflow

---

## Architecture Overview

```
[Cal.com Booking Flow]
        │
        ▼
[Chat Widget / Redirect]  ←── embedded iframe or post-booking redirect
        │
        ▼
[FastAPI Service — Mac Mini M4]
  ├── Intake Bot (fine-tuned LLM via MLX)
  ├── RAG Pipeline (LlamaIndex or LangChain)
  │     └── Vector DB (ChromaDB or LanceDB)
  │           └── Indexed: syllabi, assignments, error taxonomies
  └── Summary Generator → structured JSON / markdown
        │
        ▼
[Delivery Layer]
  ├── Cal.com booking metadata (via API)
  └── Email/notification to professor (pre-session brief)
```

---

## Phase 0: Scoping & Design Decisions

**Timeline: Week 1**

**Goal: Lock in key architectural choices before writing any code**

### 0.1 Decide Integration Point

Choose ONE to start:


| Option | Description | Tradeoff |
|--------|-------------|----------|
| **Pre-booking** | Chat before student selects a time slot | More ambitious; can shape booking intent |
| **Post-booking** | Chat after slot is confirmed (intake form UX) | Simpler; student is already committed |

> **Recommendation:** Start post-booking. Student has confirmed intent; you capture the intake data reliably. Pre-booking can be a v2 feature.

### 0.2 Define the Output Schema

Design the structured summary JSON *before* building anything. This drives the fine-tuning data format and the system prompt. Draft fields:


```json
{
  "student_id": "booking_ref",
  "appointment_date": "ISO8601",
  "course": "SPA 212-T | other",
  "primary_issue_category": "grammar | vocabulary | assignment | cultural_content | other",
  "issue_description": "Free text, 2-4 sentences",
  "specific_artifact": "e.g., 'Composition 2, paragraph 3' or 'Quiz 4, question 7'",
  "student_confidence_level": "low | medium | high",
  "professor_prep_note": "Suggested materials or context to have ready",
  "conversation_log": "Full transcript"
}
```

> Refine this schema with real booking patterns before finalizing.

### 0.3 Define Course Taxonomy

For each course you offer, document:

- Major topic/skill areas (e.g., for SPA 212-T: ser/estar, subjunctive, composition structure, cultural units)
- Common student pain points
- Assignment types and names

This becomes the backbone of both the RAG index and the fine-tuning data.

### 0.4 Scope the Dialogue Pattern

Sketch a rough flowchart of how the intake conversation should go:

1. Warm greeting + ask what course
2. Identify general area of difficulty
3. Drill down with 1-2 Socratic follow-ups
4. Confirm understanding / reflect back to student
5. Generate summary, thank student

Target: **5-8 turns max.** Longer = abandonment risk.

---

## Phase 1: Infrastructure Setup

**Timeline: Week 1–2**

**Goal: Get the local serving stack running with a baseline model**

### 1.1 Environment Setup


```bash
# Create and initialize the project
uv init intake-bot
cd intake-bot

# Create a virtual environment (uv manages this automatically on first run,
# but explicit creation lets you target a specific Python version)
uv venv --python 3.11

# Add dependencies
uv add mlx mlx-lm          # MLX ecosystem (native Apple Silicon + LoRA fine-tuning)
uv add fastapi uvicorn      # API server
uv add llama-index chromadb sentence-transformers  # RAG
uv add pydantic python-dotenv httpx  # Utilities

# Run any script within the managed environment
uv run python app/main.py

# Or activate the venv the traditional way if preferred
source .venv/bin/activate
```

> **Note:** `uv` will auto-resolve and lock dependencies into `uv.lock`. Commit this file for reproducibility. Use `uv sync` on any other machine to reproduce the exact environment.

### 1.2 Model Selection

Start with one of these; benchmark both on your Mac Mini M4:


| Model | Params | Notes |
|-------|--------|-------|
| **Llama 3.2 3B Instruct** | 3B | Fast, good instruction following, small footprint |
| **Qwen2.5 3B Instruct** | 3B | Strong multilingual (useful for Spanish context) |
| **Mistral 7B Instruct** | 7B | More capable, ~2–3x slower; worth it if quality gap is large |

> **Starting recommendation:** Qwen2.5 3B — the multilingual training could help it handle Spanish language error descriptions more naturally.

Download via MLX model hub:

```bash
mlx_lm.convert --hf-path Qwen/Qwen2.5-3B-Instruct --mlx-path ./models/qwen2.5-3b
```

### 1.3 Baseline Serving

Stand up a minimal FastAPI endpoint before any fine-tuning:


```python
# app/main.py skeleton
from fastapi import FastAPI
from mlx_lm import load, generate

app = FastAPI()
model, tokenizer = load("./models/qwen2.5-3b")

@app.post("/chat")
async def chat(payload: ChatPayload):

    response = generate(model, tokenizer, prompt=payload.prompt, max_tokens=512)
    return {"response": response}
```

Verify latency is acceptable for real-time chat (target: <2s per turn on M4).

### 1.4 Expose Local Service

Use **ngrok** or **Cloudflare Tunnel** to expose the Mac Mini to the internet for Cal.com integration:


```bash
# Cloudflare Tunnel (more stable for persistent use)
cloudflared tunnel --url http://localhost:8000
```

> Long-term: assign a static domain via Cloudflare Tunnel config so the Cal.com webhook URL doesn't change.

---

## Phase 2: RAG Pipeline

**Timeline: Week 2–3**

**Goal: Give the model grounded knowledge of your courses and materials**

### 2.1 Document Corpus

Collect and organize source documents:


```
/rag-corpus/
  /spa212/
    syllabus.pdf
    assignment_descriptions.md
    grammar_topics.md          ← create this: unit-by-unit skill list
    common_errors.md           ← create this: top 10-15 error patterns you see
  /other_courses/
    ...
  /general/
    office_hours_scope.md      ← what you can/can't help with
    referral_resources.md      ← writing center, tutoring, etc.
```

### 2.2 Indexing Pipeline


```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# Load and index documents
documents = SimpleDirectoryReader("./rag-corpus").load_data()
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("course_materials")

# Build index
index = VectorStoreIndex.from_documents(documents, ...)
```

### 2.3 RAG-Augmented Prompt Construction

At each turn, retrieve relevant context based on the conversation so far and inject into the system prompt:


```python
def build_prompt(conversation_history, retrieved_context):

    system = f"""You are a helpful intake assistant for Professor [Name]'s office hours...

COURSE CONTEXT:

{retrieved_context}

Your job is to guide the student to clearly articulate their question in 5-8 turns.
Always be warm, patient, and non-judgmental. If a student seems confused, offer
structured choices rather than open-ended questions.

OUTPUT: When ready, produce a JSON summary following this schema: {SUMMARY_SCHEMA}
"""
    return system
```

### 2.4 Test RAG Quality

Before fine-tuning, run 10-15 manual intake conversations using just the base model + RAG. Assess:

- Does it ask sensible follow-up questions?
- Does it correctly identify course areas from student descriptions?
- Does the final summary match what you'd want to see?

This establishes a baseline and identifies where fine-tuning will add the most value.

---

## Phase 3: Training Data Generation

**Timeline: Week 3–4**

**Goal: Create a fine-tuning corpus of ~300–500 synthetic intake conversations**

### 3.1 Define Student Personas

Create a matrix of persona types to ensure diversity:


| Dimension | Values |
|-----------|--------|
| Course | SPA 212-T, [other courses] |
| Self-awareness | Low (can't name the issue), Medium (knows general area), High (knows exactly) |
| Issue type | Grammar, vocabulary, composition, cultural content, assignment instructions |
| Communication style | Terse, verbose, frustrated, anxious |

### 3.2 Synthetic Data Generation Prompt

Use a frontier model (Claude or GPT-4o) to generate conversations:


```
System: You are simulating a student intake conversation for a university professor's
office hours booking system. Generate a realistic multi-turn dialogue between:

- STUDENT: [persona description from matrix]
- BOT: A warm, Socratic intake assistant

The conversation should end with the bot producing a structured JSON summary.
Follow this schema: [SUMMARY_SCHEMA]

Student persona: SPA 212 student, low self-awareness, struggling with a recent
composition assignment but can only say "I don't get it"
```

Generate ~20-30 conversations per persona combination. Budget ~$5-10 in API costs.

### 3.3 Data Curation

- Review every conversation (or a statistically representative sample)
- Edit bot turns that feel off-brand, too clinical, or too verbose
- Ensure summary JSON is well-formed and matches schema
- Convert to MLX fine-tuning JSONL format:


```jsonl
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

### 3.4 Train/Val Split

- 80% train (~250-400 examples)
- 20% validation (~60-100 examples)
- Hold out 20 real/curated conversations as a test set (do not use in training)

---

## Phase 4: Fine-Tuning with LoRA

**Timeline: Week 4–5**

**Goal: Fine-tune the base model on intake conversation patterns**

### 4.1 LoRA Config (MLX-LM)


```bash
mlx_lm.lora \
  --model ./models/qwen2.5-3b \
  --train \
  --data ./training-data/ \
  --batch-size 4 \
  --lora-layers 8 \
  --iters 1000 \
  --val-batches 25 \
  --learning-rate 1e-5 \
  --steps-per-report 50 \
  --steps-per-eval 200 \
  --save-every 500 \
  --adapter-path ./adapters/intake-bot-v1
```

### 4.2 Monitor Training

Watch for:

- Validation loss decreasing without diverging from train loss (overfitting signal)
- Qualitative spot-checks every 200 steps: does the model still follow instructions?
- Target: val loss in the 1.2–1.8 range for this task complexity

### 4.3 Fuse Adapter (for deployment)

```bash
mlx_lm.fuse \
  --model ./models/qwen2.5-3b \
  --adapter-path ./adapters/intake-bot-v1 \
  --save-path ./models/intake-bot-v1-fused
```

### 4.4 Evaluation

Test against held-out conversations:

- Does the conversation resolve in ≤8 turns?
- Is the JSON summary well-formed?
- Does the `issue_description` field accurately reflect the problem?
- Does the `professor_prep_note` provide useful context?

Score each on a 1-3 rubric, target average ≥2.5 before proceeding to integration.

---

## Phase 5: Cal.com Integration

**Timeline: Week 5–6**

**Goal: Wire the bot into the actual booking workflow**

### 5.1 Cal.com Webhook Setup

Configure Cal.com to POST a webhook on booking confirmation:


```
Settings → Webhooks → Add Webhook
URL: https://your-tunnel-url.cfargotunnel.com/booking-confirmed
Events: BOOKING_CREATED
```

Webhook payload includes: attendee name, email, booking time, event type.

### 5.2 Booking Confirmation Flow


```python
@app.post("/booking-confirmed")
async def booking_confirmed(payload: CalWebhookPayload):

    # 1. Create a session ID
    session_id = create_session(payload)

    # 2. Send intake chat link to student via email
    chat_url = f"https://your-tunnel-url/intake/{session_id}"
    send_email(payload.attendee_email, chat_url)

    return {"status": "intake initiated"}

@app.get("/intake/{session_id}")
async def intake_page(session_id: str):

    # Serve the chat widget UI
    return HTMLResponse(content=chat_widget_html(session_id))
```

### 5.3 Chat Widget UI

Build a minimal chat interface (vanilla HTML/JS or simple React):

- Clean, mobile-friendly layout (students will use phones)
- Show professor name and appointment details at top
- 5-8 turn conversation, then "Done" confirmation screen
- No login required — session_id in URL is the auth token

### 5.4 Summary Delivery

When conversation completes:

```python
def deliver_summary(session_id: str, summary: dict):

    # Option A: Email to professor
    send_email(PROFESSOR_EMAIL, format_summary_email(summary))

    # Option B: Write to Cal.com booking notes via API
    cal_api.update_booking_notes(
        booking_uid=summary["booking_ref"],
        notes=summary["professor_prep_note"]
    )

    # Option C: Both (recommended)
```

---

## Phase 6: Hardening & Iteration

**Timeline: Ongoing after initial deployment**

### 6.1 Logging & Feedback Loop

- Log all conversations (locally, with student consent disclosure)
- Add a simple thumbs up/down at end of student chat
- Review weekly; add poor conversations to next fine-tuning round

### 6.2 Guardrails

Add basic safety checks:

- If student expresses distress → redirect to campus resources
- If conversation goes off-topic → gently redirect
- Hard timeout at 10 turns → force summary generation

### 6.3 Privacy Considerations

- Add disclosure at start of chat: "This conversation will be summarized for your professor"
- Store logs locally only; no third-party cloud
- Define a retention policy (e.g., delete after 90 days)
- Consider IRB implications if you use conversation data for research

### 6.4 Planned v2 Features

- [ ] Pre-booking flow (help student decide *whether* to book)
- [ ] Multi-language support (allow students to describe issues in Spanish)
- [ ] Recurring student profile (track patterns across sessions)
- [ ] Calendar-aware context injection (upcoming assignments/exams)

---

## Tech Stack Summary


| Layer | Tool | Rationale |
|-------|------|-----------|
| LLM Runtime | MLX-LM | Native Apple Silicon; best performance on M4 |
| Base Model | Qwen2.5 3B Instruct | Small, multilingual, instruction-tuned |
| Fine-tuning | MLX-LM LoRA | Integrated with runtime; no separate framework needed |
| RAG | LlamaIndex + ChromaDB | Mature, well-documented, runs locally |
| API Server | FastAPI | Lightweight, async, easy to extend |
| Tunnel | Cloudflare Tunnel | Stable persistent URL, free tier sufficient |
| Chat UI | Vanilla HTML/JS | No build tooling; simple to maintain |
| Booking Platform | Cal.com | Existing infrastructure; webhook support |
| Package Manager | uv | Fast, lockfile-based; replaces pip/venv/poetry |
| Synthetic Data Gen | Claude / GPT-4o API | One-time cost ~$5-10 |

---

## Risk Register


| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Model quality insufficient at 3B params | Medium | High | Benchmark vs. 7B; upgrade if needed |
| Students abandon intake chat | Medium | Medium | Keep to ≤5 turns; mobile-friendly UI |
| Fine-tuning data not diverse enough | Low | Medium | Careful persona matrix coverage |
| Cloudflare tunnel instability | Low | Medium | Add health check + auto-restart |
| Student privacy concerns | Low | High | Clear disclosure; local-only storage |
| M4 thermal throttling under load | Low | Low | Single-user sequential load; unlikely issue |

---

## Open Questions

- [ ] What is the acceptable latency for students? (Target: <2s/turn)
- [ ] Should the chat link expire after a time window? (e.g., 48 hours post-booking)
- [ ] Cal.com plan level — does your current plan support webhooks?
- [ ] Will students need to be told this is AI-generated, per WFU policy?
- [ ] Do you want the summary injected back into Cal.com, emailed, or both?

---

## Revision Log


| Date | Change |
|------|--------|
| 2026-02-17 | Initial draft |
| 2026-02-17 | Updated Phase 1.1 and tech stack to use `uv` for environment/package management |
