import pytest

from src.ai_analysis import analyze_content, PROMPT_VERSION


@pytest.fixture
def good_assessment():
    """Assessment values that should not trigger concern observations."""
    return {
        "freshness": 90,
        "quality": 90,
        "performance": 90,
        "engagement": 50,
    }


@pytest.fixture
def good_content():
    """Content with no significant duplication concern."""
    return {
        "duplicate_similarity": 0.10,
    }


def test_returns_expected_structure(good_content, good_assessment):
    """The analysis should return the expected keys and data types."""
    result = analyze_content(good_content, good_assessment)

    assert set(result.keys()) == {
        "summary",
        "observations",
        "prompt_version",
    }
    assert isinstance(result["summary"], str)
    assert isinstance(result["observations"], list)
    assert len(result["observations"]) > 0
    assert result["prompt_version"] == PROMPT_VERSION


def test_flags_low_freshness(good_content, good_assessment):
    """Low freshness should trigger a freshness observation."""
    good_assessment["freshness"] = 59

    result = analyze_content(good_content, good_assessment)

    assert any(
        "dated" in observation
        for observation in result["observations"]
    )


def test_flags_low_quality(good_content, good_assessment):
    """Low quality should trigger a completeness observation."""
    good_assessment["quality"] = 69

    result = analyze_content(good_content, good_assessment)

    assert any(
        "Completeness indicators" in observation
        for observation in result["observations"]
    )


def test_flags_low_performance(good_content, good_assessment):
    """Low performance should trigger a page-experience observation."""
    good_assessment["performance"] = 59

    result = analyze_content(good_content, good_assessment)

    assert any(
        "Performance indicators" in observation
        for observation in result["observations"]
    )


def test_flags_high_duplicate_similarity(good_content, good_assessment):
    """High duplicate similarity should trigger a consolidation observation."""
    good_content["duplicate_similarity"] = 0.80

    result = analyze_content(good_content, good_assessment)

    assert any(
        "consolidation opportunity" in observation
        for observation in result["observations"]
    )


def test_flags_high_engagement(good_content, good_assessment):
    """High engagement should be considered before retirement."""
    good_assessment["engagement"] = 70

    result = analyze_content(good_content, good_assessment)

    assert any(
        "actively used" in observation
        for observation in result["observations"]
    )


def test_returns_fallback_when_no_concerns(good_content, good_assessment):
    """No triggered rules should produce the fallback observation."""
    result = analyze_content(good_content, good_assessment)

    assert result["observations"] == [
        "Available evidence does not identify a significant governance concern."
    ]


def test_summary_explains_advisory_role(good_content, good_assessment):
    """The qualitative layer should not claim to make the final decision."""
    result = analyze_content(good_content, good_assessment)

    assert "advisory" in result["summary"]
    assert "does not determine the final governance decision" in result["summary"]


def test_all_observations_can_be_returned_together():
    """Multiple concerns should be reported in a single analysis."""
    content = {
        "duplicate_similarity": 0.95,
    }
    assessment = {
        "freshness": 20,
        "quality": 40,
        "performance": 30,
        "engagement": 85,
    }

    result = analyze_content(content, assessment)

    assert len(result["observations"]) == 5


def test_handles_unavailable_assessment_scores():
    """Unavailable scores should trigger a human-review observation."""
    content = {
        "duplicate_similarity": 0.10,
    }
    assessment = {
        "freshness": None,
        "quality": None,
        "performance": None,
        "engagement": None,
    }

    result = analyze_content(content, assessment)

    assert "summary" in result
    assert "observations" in result
    assert "prompt_version" in result
    assert len(result["observations"]) == 1
    assert "Human review is required" in result["summary"]
    assert "scores could not be calculated" in result["observations"][0]
