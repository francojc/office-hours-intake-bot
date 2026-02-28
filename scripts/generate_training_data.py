#!/usr/bin/env python3
"""Generate synthetic training data from the persona matrix.

Reads training-data/persona_matrix.json, produces multi-turn
conversations following the intake dialogue flow, and writes
MLX-LM-compatible JSONL to training-data/{train,val,test}.jsonl.

Each JSONL line contains a "messages" list of
{"role": "system"|"user"|"assistant", "content": "..."} dicts,
ending with the assistant producing a JSON IntakeSummary.

Usage:
    uv run python scripts/generate_training_data.py
    uv run python scripts/generate_training_data.py --variations 3
"""

import argparse
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PERSONA_PATH = REPO_ROOT / "training-data" / "persona_matrix.json"
OUTPUT_DIR = REPO_ROOT / "training-data"
SYSTEM_PROMPT_PATH = REPO_ROOT / "docs" / "system-prompt.md"

# Conversation template fragments keyed by dialogue step.
# Each persona generates one or more synthetic conversations by
# filling these templates with persona-specific content.

GREETING_TEMPLATES = [
    "Hi {name}! I'm here to help you prepare for your appointment "
    "with Dr. Francom on {date}. To get started, what brings you in "
    "today?\n\n1. SPA 212-T (course help)\n"
    "2. Another course\n3. Something else (not course-related)",
]

COURSE_CHOICE = {
    "SPA 212-T": [
        "SPA 212-T",
        "I need help with SPA 212",
        "It's for my Spanish 212 class",
        "1",
    ],
    "other_course": [
        "Another course",
        "It's for a different Spanish class",
        "2",
    ],
    "non_course": [
        "Something else",
        "It's not about a course",
        "3",
    ],
}

CATEGORY_QUESTION = (
    "Got it — SPA 212. What area do you need help with?\n\n"
    "- Grammar or verb forms\n- Vocabulary\n"
    "- A writing assignment (composición)\n"
    "- Preparing for an exam\n"
    "- Preparing for an interview\n"
    "- Understanding a reading or cultural topic\n"
    "- Something else"
)

CATEGORY_RESPONSES = {
    "grammar": [
        "Grammar",
        "I need help with grammar",
        "Verb forms are confusing me",
    ],
    "vocabulary": [
        "Vocabulary",
        "I'm having trouble with vocab",
    ],
    "composition": [
        "A writing assignment",
        "I need help with my composición",
    ],
    "exam_prep": [
        "Preparing for an exam",
        "I have an exam coming up",
    ],
    "interview_prep": [
        "Preparing for an interview",
        "The oral interview",
    ],
    "literary_comprehension": [
        "Understanding a reading",
        "I'm confused about the reading",
    ],
    "cultural_content": [
        "Understanding a cultural topic",
        "The cultural reading is confusing",
    ],
    "assignment_instructions": [
        "Something else",
        "I don't understand the assignment instructions",
    ],
    "oral_presentation": [
        "Something else",
        "I need help with my oral presentation",
    ],
    "general": [
        "Something else",
        "I have a general question",
    ],
    "other": [
        "Something else",
        "It's kind of hard to explain",
    ],
}

GRAMMAR_DRILLDOWN = {
    "ser_estar": [
        "Ser vs. estar",
        "I keep mixing up ser and estar",
    ],
    "preterite_imperfect": [
        "Preterite vs. imperfect",
        "I don't know when to use preterite or imperfect",
    ],
    "subjunctive_triggers": [
        "Subjunctive",
        "The subjunctive — I never know when to use it",
    ],
    "subjunctive_formation": [
        "Subjunctive",
        "I can't conjugate the subjunctive forms",
    ],
    "commands_informal": [
        "Commands",
        "Informal commands",
    ],
    "commands_formal": [
        "Commands",
        "Formal commands, like usted",
    ],
    "object_pronouns": [
        "Object pronouns",
        "Direct and indirect object pronouns",
    ],
    "object_pronouns_double": [
        "Object pronouns",
        "Double object pronouns — when you have two together",
    ],
    "gustar_verbs": [
        "Gustar-type verbs",
        "Verbs like gustar",
    ],
    "conditional": [
        "Conditional and si clauses",
        "The conditional tense",
    ],
    "si_clauses": [
        "Conditional and si clauses",
        "Si clauses — the if-then stuff",
    ],
    "adverbial_clauses": [
        "I'm not sure",
        "Something about clauses but I don't know the name",
    ],
    "future_tense": [
        "I'm not sure",
        "Future tense maybe?",
    ],
}

CONFIDENCE_OPTIONS = {
    "lost": [
        "I'm totally lost — I don't even know where to start",
        "Totally lost",
        "I have no idea where to begin",
    ],
    "struggling": [
        "I'm struggling — I know the general area but can't get it right",
        "Struggling, I guess",
        "I sort of get it but I keep making mistakes",
    ],
    "mostly_ok": [
        "I'm mostly okay — I have a specific question",
        "Mostly okay, just one question",
        "I think I understand most of it",
    ],
    "just_checking": [
        "I just want to confirm I'm on the right track",
        "Just checking my work",
        "I think I've got it, I just want to make sure",
    ],
}

CONFIRM_RESPONSES = [
    "Yes, that sounds right!",
    "Yeah, that's it.",
    "Exactly.",
    "That's correct.",
    "Yep, nothing to add.",
    "That sums it up, thanks!",
]

FIRST_NAMES = [
    "Alex",
    "Jordan",
    "Taylor",
    "Morgan",
    "Casey",
    "Riley",
    "Avery",
    "Quinn",
    "Blake",
    "Skyler",
    "Jamie",
    "Reese",
    "Emerson",
    "Parker",
    "Sage",
    "Cameron",
    "Dakota",
    "Hayden",
    "Rowan",
    "Finley",
]


def load_system_prompt() -> str:
    """Load the system prompt template from docs/system-prompt.md."""
    import re

    raw = SYSTEM_PROMPT_PATH.read_text()
    match = re.search(
        r"^## Prompt\s*\n+```\n(.*?)```",
        raw,
        re.DOTALL | re.MULTILINE,
    )
    if match:
        return match.group(1).rstrip("\n")
    return raw


def random_appointment() -> tuple[str, datetime]:
    """Generate a random future appointment datetime and name."""
    name = random.choice(FIRST_NAMES)
    base = datetime.now(tz=timezone.utc) + timedelta(days=random.randint(1, 14))
    hour = random.choice([9, 10, 11, 13, 14, 15, 16])
    apt = base.replace(hour=hour, minute=0, second=0, microsecond=0)
    return name, apt


def build_spa212_conversation(
    persona: dict, name: str, apt: datetime
) -> list[dict]:
    """Build a multi-turn conversation for a SPA 212-T persona."""
    messages = []
    cat = persona["issue_category"]
    subcat = persona.get("issue_subcategory")
    artifact = persona.get("specific_artifact")
    sa = persona.get("self_assessment")
    date_str = apt.strftime("%A, %B %d at %I:%M %p")

    # Turn 1: Greeting
    messages.append(
        {
            "role": "assistant",
            "content": random.choice(GREETING_TEMPLATES).format(
                name=name, date=date_str
            ),
        }
    )
    messages.append(
        {
            "role": "user",
            "content": random.choice(COURSE_CHOICE["SPA 212-T"]),
        }
    )

    # Turn 2: Category
    messages.append(
        {
            "role": "assistant",
            "content": CATEGORY_QUESTION,
        }
    )
    cat_responses = CATEGORY_RESPONSES.get(cat, CATEGORY_RESPONSES["other"])
    messages.append(
        {
            "role": "user",
            "content": random.choice(cat_responses),
        }
    )

    # Turn 3: Drill-down (grammar-specific or generic)
    if cat == "grammar" and subcat and subcat in GRAMMAR_DRILLDOWN:
        messages.append(
            {
                "role": "assistant",
                "content": (
                    "Which grammar topic is giving you trouble?\n\n"
                    "- Ser vs. estar\n- Preterite vs. imperfect\n"
                    "- Subjunctive\n- Commands (formal/informal)\n"
                    "- Object pronouns\n- Gustar-type verbs\n"
                    "- Conditional and si clauses\n- I'm not sure"
                ),
            }
        )
        messages.append(
            {
                "role": "user",
                "content": random.choice(GRAMMAR_DRILLDOWN[subcat]),
            }
        )
    elif cat == "exam_prep" and artifact:
        messages.append(
            {
                "role": "assistant",
                "content": (
                    "Which exam are you preparing for?\n\n"
                    "- Exam 1 (Chapters 1-2)\n"
                    "- Exam 2 (Chapters 3-4)\n"
                    "- Exam 3 / Final (Chapters 5-6)"
                ),
            }
        )
        messages.append(
            {
                "role": "user",
                "content": artifact,
            }
        )
    elif cat == "composition" and subcat:
        sub_label = {
            "composition_thesis": ("Understanding the prompt / instructions"),
            "composition_organization": "Organizing my ideas or thesis",
            "composition_grammar": "Grammar issues in my writing",
        }.get(subcat, "I'm not sure")
        messages.append(
            {
                "role": "assistant",
                "content": (
                    "What part of the composition are you working on?\n\n"
                    "- Understanding the prompt / instructions\n"
                    "- Organizing my ideas or thesis\n"
                    "- Grammar issues in my writing\n"
                    "- I've written a draft and want feedback guidance"
                ),
            }
        )
        messages.append({"role": "user", "content": sub_label})
    else:
        messages.append(
            {
                "role": "assistant",
                "content": (
                    "Can you tell me a bit more about what's going on? "
                    "Is there a specific topic or assignment?"
                ),
            }
        )
        detail = persona.get("notes", "I'm just stuck.")
        messages.append({"role": "user", "content": detail})

    # Turn 4: Specific artifact (skip if already mentioned)
    if artifact and artifact not in str(messages):
        messages.append(
            {
                "role": "assistant",
                "content": (
                    "Is there a specific assignment or exercise "
                    'connected to this? For example, "Escritura I" '
                    'or "ED 8" or "Chapter 3 practice."'
                ),
            }
        )
        messages.append({"role": "user", "content": artifact})

    # Turn 5: Confidence check
    if sa and sa in CONFIDENCE_OPTIONS:
        messages.append(
            {
                "role": "assistant",
                "content": (
                    'On a scale from "totally lost" to '
                    '"just want to double-check," where would you '
                    "put yourself?\n\n"
                    "- I'm totally lost\n- I'm struggling\n"
                    "- I'm mostly okay\n"
                    "- I just want to confirm I'm on the right track"
                ),
            }
        )
        messages.append(
            {
                "role": "user",
                "content": random.choice(CONFIDENCE_OPTIONS[sa]),
            }
        )

    # Turn 6: Reflection and confirmation
    subcat_display = (
        subcat.replace("_", " ") if subcat else cat.replace("_", " ")
    )
    artifact_mention = f" for {artifact}" if artifact else ""
    sa_display = {
        "lost": "totally lost",
        "struggling": "struggling a bit",
        "mostly_ok": "mostly okay with a specific question",
        "just_checking": "just looking to confirm",
    }.get(sa or "", "")

    reflection = (
        f"Here's what I'm hearing: you're working on "
        f"{subcat_display}{artifact_mention}"
    )
    if sa_display:
        reflection += f", and you're feeling {sa_display} about it"
    reflection += ". Does that sound right, or would you like to add anything?"

    messages.append({"role": "assistant", "content": reflection})
    messages.append(
        {
            "role": "user",
            "content": random.choice(CONFIRM_RESPONSES),
        }
    )

    # Turn 7: Closing + JSON summary
    closing = (
        f"Thanks for sharing all of that! I'll send a summary to "
        f"Dr. Francom so he can prepare for your appointment. "
        f"See you on {date_str}!"
    )

    summary = build_summary_json(persona, name, apt, len(messages) // 2)
    closing += "\n\n" + json.dumps(summary, indent=2)
    messages.append({"role": "assistant", "content": closing})

    return messages


def build_non_course_conversation(
    persona: dict, name: str, apt: datetime
) -> list[dict]:
    """Build a short non-course conversation."""
    messages = []
    date_str = apt.strftime("%A, %B %d at %I:%M %p")

    # Turn 1
    messages.append(
        {
            "role": "assistant",
            "content": random.choice(GREETING_TEMPLATES).format(
                name=name, date=date_str
            ),
        }
    )
    messages.append(
        {
            "role": "user",
            "content": random.choice(COURSE_CHOICE["non_course"]),
        }
    )

    # Turn 2: Meeting purpose
    messages.append(
        {
            "role": "assistant",
            "content": (
                "No problem! Can you give me a brief idea of what "
                "you'd like to discuss? Just a sentence or two is fine."
            ),
        }
    )
    messages.append(
        {
            "role": "user",
            "content": persona.get(
                "notes", "I'd like to discuss a research collaboration."
            ),
        }
    )

    # Turn 3: Anything to prepare
    messages.append(
        {
            "role": "assistant",
            "content": (
                "Is there anything specific you'd like Dr. Francom "
                "to have ready or review beforehand?"
            ),
        }
    )
    messages.append(
        {
            "role": "user",
            "content": "Nothing specific, thanks.",
        }
    )

    # Turn 4: Closing
    summary = build_summary_json(persona, name, apt, 4)
    closing = (
        f"Got it — I'll pass that along so Dr. Francom can prepare. "
        f"See you on {date_str}!"
        f"\n\n{json.dumps(summary, indent=2)}"
    )
    messages.append({"role": "assistant", "content": closing})

    return messages


def build_other_course_conversation(
    persona: dict, name: str, apt: datetime
) -> list[dict]:
    """Build a conversation for a non-SPA-212 course."""
    messages = []
    date_str = apt.strftime("%A, %B %d at %I:%M %p")

    # Turn 1
    messages.append(
        {
            "role": "assistant",
            "content": random.choice(GREETING_TEMPLATES).format(
                name=name, date=date_str
            ),
        }
    )
    messages.append(
        {
            "role": "user",
            "content": random.choice(COURSE_CHOICE["other_course"]),
        }
    )

    # Turn 2: What area
    messages.append(
        {
            "role": "assistant",
            "content": "What area do you need help with?",
        }
    )
    messages.append(
        {
            "role": "user",
            "content": persona.get("notes", "I need help with grammar."),
        }
    )

    # Turn 3: Specific artifact
    artifact = persona.get("specific_artifact")
    if artifact:
        messages.append(
            {
                "role": "assistant",
                "content": (
                    "Is there a specific assignment or exercise "
                    "connected to this?"
                ),
            }
        )
        messages.append({"role": "user", "content": artifact})

    # Turn 4: Confidence
    sa = persona.get("self_assessment")
    if sa and sa in CONFIDENCE_OPTIONS:
        messages.append(
            {
                "role": "assistant",
                "content": (
                    "How are you feeling about this topic — totally "
                    "lost, struggling, mostly okay, or just checking?"
                ),
            }
        )
        messages.append(
            {
                "role": "user",
                "content": random.choice(CONFIDENCE_OPTIONS[sa]),
            }
        )

    # Turn 5: Confirmation
    messages.append(
        {
            "role": "assistant",
            "content": (
                "Got it. Let me make sure I have this right — you "
                "need help with your course work. Does that cover it?"
            ),
        }
    )
    messages.append(
        {
            "role": "user",
            "content": random.choice(CONFIRM_RESPONSES),
        }
    )

    # Closing
    summary = build_summary_json(persona, name, apt, len(messages) // 2)
    closing = (
        f"Thanks! I'll send a summary to Dr. Francom. "
        f"See you on {date_str}!"
        f"\n\n{json.dumps(summary, indent=2)}"
    )
    messages.append({"role": "assistant", "content": closing})

    return messages


def build_summary_json(
    persona: dict, name: str, apt: datetime, turn_count: int
) -> dict:
    """Build the IntakeSummary JSON dict from a persona."""
    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    booking_ref = f"cal-{uuid.uuid4().hex[:6]}"
    notes = persona.get("notes", "")

    # Build a plausible issue_description from persona notes
    issue_desc = notes if notes else "Student needs general help."

    # Build a prep note
    subcat = persona.get("issue_subcategory")
    cat = persona["issue_category"]
    if subcat:
        prep_note = f"Review {subcat.replace('_', ' ')} materials. {notes}"
    else:
        prep_note = f"Prepare for a {cat.replace('_', ' ')} discussion. {notes}"

    return {
        "session_id": session_id,
        "booking_ref": booking_ref,
        "appointment_datetime": apt.isoformat(),
        "course": persona["course"],
        "issue_category": cat,
        "issue_subcategory": subcat,
        "specific_artifact": persona.get("specific_artifact"),
        "issue_description": issue_desc,
        "student_self_assessment": persona.get("self_assessment"),
        "professor_prep_note": prep_note,
        "turn_count": turn_count,
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
    }


def generate_conversation(persona: dict) -> list[dict]:
    """Generate a full conversation from a persona."""
    name, apt = random_appointment()
    course = persona["course"]

    if course == "SPA 212-T":
        turns = build_spa212_conversation(persona, name, apt)
    elif course == "non_course":
        turns = build_non_course_conversation(persona, name, apt)
    else:
        turns = build_other_course_conversation(persona, name, apt)

    # Prepend system message with placeholder context
    system_content = (
        "You are an intake assistant for Dr. Jerid Francom's "
        "office hours at Wake Forest University. Follow the "
        "intake dialogue flow to gather information and produce "
        "a structured JSON summary."
    )
    return [{"role": "system", "content": system_content}] + turns


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic training data from persona matrix"
    )
    parser.add_argument(
        "--variations",
        type=int,
        default=5,
        help="Number of conversation variations per persona (default: 5)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="0.8,0.1,0.1",
        help="Train/val/test split ratios (default: 0.8,0.1,0.1)",
    )
    args = parser.parse_args()

    random.seed(args.seed)
    ratios = [float(r) for r in args.split.split(",")]
    assert len(ratios) == 3, "Split must have exactly 3 values"

    # Load persona matrix
    with open(PERSONA_PATH) as f:
        matrix = json.load(f)

    personas = matrix["personas"]
    print(f"Loaded {len(personas)} personas")

    # Generate conversations
    all_convos = []
    for persona in personas:
        for _ in range(args.variations):
            convo = generate_conversation(persona)
            all_convos.append({"messages": convo})

    random.shuffle(all_convos)
    total = len(all_convos)
    print(f"Generated {total} conversations")

    # Split into train/val/test
    train_end = int(total * ratios[0])
    val_end = train_end + int(total * ratios[1])

    splits = {
        "train.jsonl": all_convos[:train_end],
        "valid.jsonl": all_convos[train_end:val_end],
        "test.jsonl": all_convos[val_end:],
    }

    for filename, convos in splits.items():
        path = OUTPUT_DIR / filename
        with open(path, "w") as f:
            for convo in convos:
                f.write(json.dumps(convo) + "\n")
        print(f"Wrote {len(convos)} conversations to {path.name}")

    print("Done.")


if __name__ == "__main__":
    main()
