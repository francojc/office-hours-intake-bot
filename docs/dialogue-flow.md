# Intake Dialogue Flow

Target: 5-8 turns. Hard cutoff at 10.

## Turn-by-Turn Structure

### Turn 1: Greeting and Course Identification

Bot opens with a warm greeting, identifies the appointment, and asks
which course the student needs help with.

```
Bot: Hi [name]! I'm here to help you prepare for your appointment
     with Dr. Francom on [date]. To get started, what brings you in?
     - SPA 212-T (course help)
     - Another course
     - Something else (not course-related)
```

**If "Another course":** record `course: "other_course"` and proceed
with a general open-ended flow (skip taxonomy-specific follow-ups).

**If "Something else":** record `course: "non_course"` and skip to the
non-course flow (see below).

### Turn 2: Issue Category

Ask the student to pick a general area. Offer structured choices to
reduce friction, especially for students who "don't know what they
don't know."

```
Bot: Got it — SPA 212. What area do you need help with?
     - Grammar or verb forms
     - Vocabulary
     - A writing assignment (composición)
     - Preparing for an exam
     - Preparing for an interview
     - Understanding a reading or cultural topic
     - Something else
```

Map the selection to `issue_category`. If "something else," ask a brief
open-ended follow-up: "Can you describe what's going on?"

### Turn 3: Drill-Down (Socratic Follow-Up 1)

Based on the category, ask a targeted follow-up. Use the course taxonomy
to offer specific options.

**Grammar example:**

```
Bot: Which grammar topic is giving you trouble?
     - Ser vs. estar
     - Preterite vs. imperfect
     - Subjunctive (reactions, recommendations, doubt)
     - Commands (formal/informal)
     - Object pronouns
     - Gustar-type verbs
     - Conditional and si clauses
     - I'm not sure
```

**Composition example:**

```
Bot: What part of the composition are you working on?
     - Understanding the prompt / instructions
     - Organizing my ideas or thesis
     - Grammar issues in my writing
     - I've written a draft and want feedback guidance
```

**Exam prep example:**

```
Bot: Which exam are you preparing for, and is there a specific topic?
     - Exam 1 (Chapters 1-2: descriptions, narration)
     - Exam 2 (Chapters 3-4: subjunctive, pronouns, gustar)
     - Exam 3 / Final (Chapters 5-6: conditional, si clauses, synthesis)
```

If the student selects "I'm not sure," move to Turn 3a.

### Turn 3a: Guided Discovery (for "I'm not sure" responses)

Help the student narrow down the issue with a concrete scenario.

```
Bot: No problem — let's figure it out together. Can you point me to
     a specific assignment, exercise, or moment in class where you
     felt stuck? For example:
     - A homework exercise or ED activity
     - A section of a composition draft
     - Something from a recent class or video
     - I just feel generally behind
```

Use the answer to infer `issue_category` and `issue_subcategory`.

### Turn 4: Specific Artifact

Ask what specific assignment, exercise, or material is involved.
Skip this turn if the student already mentioned something concrete.

```
Bot: Is there a specific assignment or exercise connected to this?
     For example, "Escritura I" or "ED 8" or "Chapter 3 practice."
     If not, that's fine too.
```

Record in `specific_artifact`. Accept free-text input.

### Turn 5: Confidence Check

Gauge how the student feels about the topic. Frame it without judgment.

```
Bot: On a scale from "totally lost" to "just want to double-check,"
     where would you put yourself?
     - I'm totally lost — I don't even know where to start
     - I'm struggling — I know the general area but can't get it right
     - I'm mostly okay — I have a specific question
     - I just want to confirm I'm on the right track
```

Map to `student_self_assessment`.

### Turn 6: Reflection and Confirmation

Summarize what the bot has gathered and ask the student to confirm or
correct.

```
Bot: Here's what I'm hearing: you're working on [topic] for
     [assignment], and you're feeling [confidence level] about it.
     Does that sound right, or would you like to add anything?
```

If the student corrects something, update the relevant fields and
re-confirm (Turn 6a, counts toward the 10-turn limit).

### Turn 7: Closing

Thank the student and let them know the summary is being sent.

```
Bot: Thanks for sharing all of that! I'll send a summary to
     Dr. Francom so he can prepare for your appointment. See you
     on [date]!
```

Generate the `IntakeSummary` JSON and trigger delivery.

## Non-Course Flow

When the visitor selects "Something else," the bot switches to a
lightweight flow for colleague meetings, advisee check-ins, or other
non-course-specific conversations.

### Turn 2 (non-course): Meeting Purpose

```
Bot: No problem! Can you give me a brief idea of what you'd like to
     discuss? Just a sentence or two is fine.
```

Accept free-text input. Record in `issue_description`. Set
`issue_category: "general"` and `issue_subcategory: null`.

### Turn 3 (non-course): Anything to Prepare

```
Bot: Is there anything specific you'd like Dr. Francom to have ready
     or review beforehand?
```

Record in `professor_prep_note`. Accept free-text or "Nothing specific."

### Turn 4 (non-course): Closing

```
Bot: Got it — I'll pass that along so Dr. Francom can prepare.
     See you on [date]!
```

Generate the `IntakeSummary` with `student_self_assessment: null` and
`specific_artifact: null`. The non-course flow should complete in 3-4
turns.

> **Future work:** If non-course meetings become frequent, populate
> `rag-corpus/general/non_course_meetings.md` with relevant context
> (e.g., advising resources, committee information, common meeting
> topics) and wire it into the RAG pipeline for this flow.

---

## Edge Cases

### Student expresses distress or personal crisis

If the student mentions emotional distress, mental health concerns, or
personal crisis language, the bot should:

1. Acknowledge warmly: "It sounds like you're going through a tough
   time."
2. Redirect to resources: "The WFU Counseling Center (336-758-5273)
   is a great place to get support."
3. Still offer to continue the intake if the student wants to.
4. Flag `professor_prep_note` with the concern (without diagnostic
   language).

### Student goes off-topic

If a course-flow visitor's input is unrelated to coursework:

```
Bot: I appreciate you sharing that! If this isn't about a specific
     course, you can go back and pick "Something else" to let
     Dr. Francom know what you'd like to discuss. Otherwise, is
     there something course-related I can help you get ready for?
```

Allow one redirect. If still off-topic, close gracefully and generate
a minimal summary.

### Student gives single-word or very terse responses

Switch from open-ended questions to multiple-choice options. Offer
concrete examples rather than asking them to describe the problem.

### Student provides too much detail in one turn

Extract the key information, confirm it, and skip intervening turns.
The bot should not rigidly follow all 7 turns if the student has
already provided everything needed.

### Turn limit reached (10 turns)

```
Bot: I want to make sure I get this to Dr. Francom in time. Let me
     wrap up the summary with what we've covered so far.
```

Force summary generation with whatever information has been gathered.
Fill in missing fields with reasonable defaults or "not specified."

### Student has multiple issues

Focus on the primary issue. Note secondary concerns in
`professor_prep_note`:

"Primary issue is subjunctive triggers for Exam 2. Student also
mentioned confusion about Escritura I prompt."
