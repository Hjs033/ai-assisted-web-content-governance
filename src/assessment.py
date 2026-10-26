from datetime import datetime

CRITERIA_VERSION = "1.0"

CONTEXTUAL_RULES = {
    "strategic_evergreen_types": ["About", "Organizational"],
    "strategic_importance_levels": ["Critical"],
}
# ---------------------------------------------------------------------------
# Individual criterion scoring functions
# Each function returns a score from 0–100.
# ---------------------------------------------------------------------------

def validate_update_date(last_updated):
    """Validate a content update date.

    Returns:
        tuple: (is_valid, message)

    A valid date must use YYYY-MM-DD format and must not be
    in the future.
    """
    if not last_updated:
        return False, "The last-updated date is missing."

    try:
        update_date = datetime.strptime(last_updated, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return (
            False,
            "The last-updated date must use YYYY-MM-DD format.",
        )

    if update_date > datetime.now().date():
        return False, "The last-updated date cannot be in the future."

    return True, ""


def freshness_score(last_updated):
    """Score content freshness based on days since last update.

    Raises:
        ValueError: If the update date is missing, malformed,
            or in the future.
    """
    is_valid, message = validate_update_date(last_updated)

    if not is_valid:
        raise ValueError(message)

    update_date = datetime.strptime(last_updated, "%Y-%m-%d").date()
    days = (datetime.now().date() - update_date).days

    if days <= 180:
        return 100
    if days <= 365:
        return 80
    if days <= 730:
        return 55

    return 25


def quality_score(row):
    """Score content quality using completeness."""
    return min(100, row["completeness"] * 100)


def performance_score(row):
    """Use the normalized performance score supplied by the dataset."""
    return min(100, max(0, row["performance_score"]))


def duplication_score(row):
    """Convert similarity into a uniqueness score."""
    return max(0, 100 - row["duplicate_similarity"] * 100)


def engagement_score(row):
    """Convert engagement rate into a 0–100 score."""
    return min(100, max(0, row["engagement_rate"] * 1000))


# ---------------------------------------------------------------------------
# Assessment criteria configuration
#
# Adding a future criterion should require:
# 1. A scoring function.
# 2. One entry in this configuration.
#
# The core assessment engine does not need to be rewritten.
# ---------------------------------------------------------------------------

ASSESSMENT_CRITERIA = [
    {
        "name": "freshness",
        "weight": 0.20,
        "scorer": lambda row: freshness_score(row["last_updated"]),
    },
    {
        "name": "quality",
        "weight": 0.20,
        "scorer": quality_score,
    },
    {
        "name": "performance",
        "weight": 0.20,
        "scorer": performance_score,
    },
    {
        "name": "duplication",
        "weight": 0.15,
        "scorer": duplication_score,
    },
    {
        "name": "engagement",
        "weight": 0.25,
        "scorer": engagement_score,
    },
]


def validate_criteria():
    """
    Validate the assessment configuration before scoring content.

    The criteria weights must add up to 1.0 so that the resulting
    health score remains normalized to a 0–100 scale.
    """
    total_weight = sum(criteria["weight"] for criteria in ASSESSMENT_CRITERIA)

    if abs(total_weight - 1.0) > 0.0001:
        raise ValueError(
            f"Assessment criteria weights must total 1.0. "
            f"Current total: {total_weight}"
        )


def calculate_health_score(row):
    """
    Calculate the weighted health score using the configured criteria.
    """
    validate_criteria()

    scores = {}

    for criterion in ASSESSMENT_CRITERIA:
        scores[criterion["name"]] = criterion["scorer"](row)

    weighted_score = sum(
        scores[criterion["name"]] * criterion["weight"]
        for criterion in ASSESSMENT_CRITERIA
    )

    return round(weighted_score), scores


# ---------------------------------------------------------------------------
# Recommendation logic
#
# Recommendation is intentionally separate from the health score.
# The health score describes content condition; the recommendation
# describes the lifecycle action that should be considered.
# ---------------------------------------------------------------------------

def determine_recommendation(row, scores, health_score):
    """
    Determine the preliminary lifecycle recommendation.

    Contextual rules are applied before generic recommendation rules.
    The result remains a system recommendation only; human review
    determines the final governance decision.
    """

    content_type = row.get("content_type", "")
    strategic_importance = row.get("strategic_importance", "")

    is_strategic_evergreen = (
        content_type in CONTEXTUAL_RULES["strategic_evergreen_types"]
        and strategic_importance
        in CONTEXTUAL_RULES["strategic_importance_levels"]
    )

    if row["duplicate_similarity"] >= 0.80:
        return (
            "Consolidate",
            "High content similarity indicates that this page may overlap substantially with another resource."
        )

    if is_strategic_evergreen and scores["freshness"] < 40:
        return (
            "Review",
            "Contextual rule applied: this content is strategically critical and organizational/evergreen in nature. "
            "The freshness concern should be evaluated through human review rather than treated as an automatic update trigger."
        )

    if scores["freshness"] < 40 or scores["quality"] < 60:
        return (
            "Update",
            "The assessment identified a significant freshness or content-quality concern that warrants an update review."
        )

    if health_score < 60:
        return (
            "Review",
            "The overall health score indicates that the content warrants additional human review."
        )

    return (
        "Keep",
        "The assessment does not identify a significant lifecycle concern based on the configured criteria."
    )

def assess_content(row):
    """
    Perform the deterministic content health assessment.

    Invalid update dates prevent scoring and require human review.
    Valid dates proceed through the normal assessment process.
    """

    is_valid, date_message = validate_update_date(row.get("last_updated"))

    if not is_valid:
        return {
            "content_id": row["content_id"],
            "title": row["title"],
            "freshness": None,
            "quality": None,
            "performance": None,
            "duplication": None,
            "engagement": None,
            "health_score": None,
            "system_status": "Requires review",
            "preliminary_recommendation": "Review",
            "recommendation_rationale": (
                f"Assessment could not be completed because {date_message} "
                "A human reviewer must verify the update date before "
                "a content health score can be assigned."
            ),
            "criteria_version": CRITERIA_VERSION,
        }

    health_score, scores = calculate_health_score(row)

    recommendation, recommendation_rationale = determine_recommendation(
        row,
        scores,
        health_score,
    )

    status = "Healthy" if health_score >= 75 else "Needs attention"

    return {
        "content_id": row["content_id"],
        "title": row["title"],
        "freshness": scores["freshness"],
        "quality": scores["quality"],
        "performance": scores["performance"],
        "duplication": scores["duplication"],
        "engagement": scores["engagement"],
        "health_score": health_score,
        "system_status": status,
        "preliminary_recommendation": recommendation,
        "recommendation_rationale": recommendation_rationale,
        "criteria_version": CRITERIA_VERSION,
    }