import sys
sys.path.append("src")
from assessment import assess_content

def test_duplicate_content_recommends_consolidation():
    row = {
        "content_id":"TEST-001","title":"Duplicate","last_updated":"2026-01-01",
        "page_views":100,"engagement_rate":.02,"word_count":500,
        "completeness":.80,"duplicate_similarity":.90,"performance_score":80
    }
    result = assess_content(row)
    assert result["preliminary_recommendation"] == "Consolidate"

def test_fresh_complete_content_can_be_kept():
    row = {
        "content_id":"TEST-002","title":"Healthy","last_updated":"2026-08-01",
        "page_views":1000,"engagement_rate":.08,"word_count":1000,
        "completeness":.95,"duplicate_similarity":.10,"performance_score":90
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