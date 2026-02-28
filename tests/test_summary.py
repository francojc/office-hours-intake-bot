from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.summary import (
    CourseType,
    IntakeSummary,
    IssueCategory,
    SelfAssessment,
)


def _valid_summary(**overrides):
    """Return kwargs for a valid IntakeSummary, with optional overrides."""
    defaults = {
        "session_id": "sess-001",
        "booking_ref": "cal-abc123",
        "appointment_datetime": datetime(
            2026, 3, 5, 14, 0, tzinfo=timezone.utc
        ),
        "course": CourseType.spa_212,
        "issue_category": IssueCategory.grammar,
        "issue_subcategory": "ser_estar",
        "specific_artifact": "ED 8",
        "issue_description": (
            "Student confuses ser and estar when describing "
            "locations. Consistently uses ser for temporary "
            "states."
        ),
        "student_self_assessment": SelfAssessment.struggling,
        "professor_prep_note": (
            "Bring ser/estar contrast examples with "
            "location vs. identity contexts."
        ),
        "turn_count": 6,
        "created_at": datetime(2026, 3, 5, 13, 50, tzinfo=timezone.utc),
    }
    defaults.update(overrides)
    return defaults


def test_valid_summary_roundtrips():
    summary = IntakeSummary(**_valid_summary())
    assert summary.session_id == "sess-001"
    assert summary.course == CourseType.spa_212
    assert summary.issue_category == IssueCategory.grammar
    assert summary.turn_count == 6


def test_nullable_fields_accept_none():
    summary = IntakeSummary(
        **_valid_summary(
            issue_subcategory=None,
            specific_artifact=None,
            student_self_assessment=None,
        )
    )
    assert summary.issue_subcategory is None
    assert summary.specific_artifact is None
    assert summary.student_self_assessment is None


def test_non_course_summary():
    summary = IntakeSummary(
        **_valid_summary(
            course=CourseType.non_course,
            issue_category=IssueCategory.general,
            issue_subcategory=None,
            specific_artifact=None,
            student_self_assessment=None,
            turn_count=3,
        )
    )
    assert summary.course == CourseType.non_course
    assert summary.student_self_assessment is None


def test_invalid_course_rejected():
    with pytest.raises(ValidationError):
        IntakeSummary(**_valid_summary(course="INVALID_COURSE"))


def test_invalid_category_rejected():
    with pytest.raises(ValidationError):
        IntakeSummary(**_valid_summary(issue_category="not_a_category"))


def test_turn_count_boundaries():
    IntakeSummary(**_valid_summary(turn_count=1))
    IntakeSummary(**_valid_summary(turn_count=10))

    with pytest.raises(ValidationError):
        IntakeSummary(**_valid_summary(turn_count=0))

    with pytest.raises(ValidationError):
        IntakeSummary(**_valid_summary(turn_count=11))


def test_json_serialization():
    summary = IntakeSummary(**_valid_summary())
    data = summary.model_dump(mode="json")
    assert data["course"] == "SPA 212-T"
    assert data["issue_category"] == "grammar"
    assert data["student_self_assessment"] == "struggling"
    roundtripped = IntakeSummary.model_validate(data)
    assert roundtripped == summary


def test_all_issue_categories():
    for cat in IssueCategory:
        summary = IntakeSummary(**_valid_summary(issue_category=cat))
        assert summary.issue_category == cat


def test_all_self_assessments():
    for sa in SelfAssessment:
        summary = IntakeSummary(**_valid_summary(student_self_assessment=sa))
        assert summary.student_self_assessment == sa
