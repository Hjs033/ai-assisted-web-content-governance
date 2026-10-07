import sys
from datetime import datetime, timedelta

import pytest

sys.path.append("src")

from assessment import (
    ASSESSMENT_CRITERIA,
    assess_content,
    freshness_score,
    validate_criteria,
)


def test_duplicate_content_recommends_consolidation():
    row = {
        "content_id": "TEST-001",
        "title": "Duplicate",
        "last_updated": "2026-01-01",
        "page_views": 100,
        "engagement_rate": .02,
        "word_count": 500,
        "completeness": .80,
        "duplicate_similarity": .90,
        "performance_score": 80
    }

    result = assess_content(row)

    assert result["preliminary_recommendation"] == "Consolidate"


def test_fresh_complete_content_can_be_kept():
    row = {
        "content_id": "TEST-002",
        "title": "Healthy",
        "last_updated": "2026-08-01",
        "page_views": 1000,
        "engagement_rate": .08,
        "word_count": 1000,
        "completeness": .95,
        "duplicate_similarity": .10,
        "performance_score": 90
    }

    result = assess_content(row)

    assert result["preliminary_recommendation"] == "Keep"


def test_critical_about_content_with_low_freshness_recommends_review():

    row = {
        "content_id": "TEST-003",
        "title": "About the Organization",
        "last_updated": "2024-03-15",
        "page_views": 6800,
        "engagement_rate": .018,
        "word_count": 1200,
        "completeness": .98,
        "duplicate_similarity": .05,
        "performance_score": 97,
        "content_type": "About",
        "strategic_importance": "Critical"
    }

    result = assess_content(row)

    assert result["preliminary_recommendation"] == "Review"
    assert "strategically critical" in result["recommendation_rationale"]


def test_non_strategic_old_content_with_low_freshness_recommends_update():

    row = {
        "content_id": "TEST-004",
        "title": "Older Workforce Report",
        "last_updated": "2022-06-15",
        "page_views": 900,
        "engagement_rate": .012,
        "word_count": 4800,
        "completeness": .61,
        "duplicate_similarity": .77,
        "performance_score": 58,
        "content_type": "Report",
        "strategic_importance": "Standard"
    }

    result = assess_content(row)

    assert result["preliminary_recommendation"] == "Update"
    assert "freshness" in result["recommendation_rationale"]


def test_freshness_score_for_intermediate_age_content():
    """Content 366–730 days old receives the intermediate freshness score."""
    date_366_days_ago = (
        datetime.now() - timedelta(days=366)
    ).strftime("%Y-%m-%d")

    assert freshness_score(date_366_days_ago) == 55


def test_validate_criteria_rejects_invalid_weights(monkeypatch):
    """Invalid assessment weights should raise a ValueError."""

    invalid_criteria = [
        {
            "name": "freshness",
            "weight": 0.50,
            "scorer": lambda row: 100,
        },
        {
            "name": "quality",
            "weight": 0.50,
            "scorer": lambda row: 100,
        },
        {
            "name": "performance",
            "weight": 0.50,
            "scorer": lambda row: 100,
        },
    ]

    monkeypatch.setattr(
        "assessment.ASSESSMENT_CRITERIA",
        invalid_criteria
    )

    with pytest.raises(ValueError, match="must total 1.0"):
        validate_criteria()


def test_low_health_score_recommends_review():

    row = {
        "content_id": "TEST-005",
        "title": "Low Health Content",
        "last_updated": "2026-09-01",
        "page_views": 100,
        "engagement_rate": .01,
        "word_count": 1000,
        "completeness": .80,
        "duplicate_similarity": .10,
        "performance_score": 20,
        "content_type": "Report",
        "strategic_importance": "Standard"
    }

    result = assess_content(row)

    assert result["health_score"] < 60
    assert result["preliminary_recommendation"] == "Review"
    assert "overall health score" in result["recommendation_rationale"]