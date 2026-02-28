"""Pydantic models for the intake summary schema."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CourseType(str, Enum):
    spa_212 = "SPA 212-T"
    other_course = "other_course"
    non_course = "non_course"


class IssueCategory(str, Enum):
    grammar = "grammar"
    vocabulary = "vocabulary"
    composition = "composition"
    exam_prep = "exam_prep"
    interview_prep = "interview_prep"
    oral_presentation = "oral_presentation"
    literary_comprehension = "literary_comprehension"
    cultural_content = "cultural_content"
    assignment_instructions = "assignment_instructions"
    general = "general"
    other = "other"


class SelfAssessment(str, Enum):
    lost = "lost"
    struggling = "struggling"
    mostly_ok = "mostly_ok"
    just_checking = "just_checking"


class IntakeSummary(BaseModel):
    """Structured summary produced after an intake conversation."""

    session_id: str = Field(
        description="Unique identifier for this intake session."
    )
    booking_ref: str = Field(
        description=(
            "Cal.com booking reference linking this session to the appointment."
        )
    )
    appointment_datetime: datetime = Field(
        description="Scheduled appointment time in ISO 8601 format."
    )
    course: CourseType = Field(
        description=(
            "Context for the meeting. 'SPA 212-T' for that course, "
            "'other_course' for a different course, 'non_course' for "
            "colleague meetings or non-course-specific conversations."
        )
    )
    issue_category: IssueCategory = Field(
        description="Primary category of the student's issue."
    )
    issue_subcategory: str | None = Field(
        default=None,
        description=(
            "Specific topic within the category, e.g. "
            "'ser_estar', 'preterite_imperfect'. "
            "Null if not applicable."
        ),
    )
    specific_artifact: str | None = Field(
        default=None,
        description=(
            "The specific assignment, exam, chapter, or exercise "
            "the student references. Null if none mentioned."
        ),
    )
    issue_description: str = Field(
        description=(
            "2-4 sentence summary of the student's issue "
            "in the bot's own words."
        )
    )
    student_self_assessment: SelfAssessment | None = Field(
        default=None,
        description=(
            "How confident the visitor feels about the topic. "
            "Null for non-course meetings."
        ),
    )
    professor_prep_note: str = Field(
        description=(
            "1-3 sentence note suggesting what materials or "
            "approach the professor should prepare."
        )
    )
    turn_count: int = Field(
        ge=1, le=10, description="Number of conversation turns."
    )
    created_at: datetime = Field(
        description="Timestamp when this summary was generated."
    )
