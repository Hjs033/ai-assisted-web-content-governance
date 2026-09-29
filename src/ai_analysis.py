PROMPT_VERSION = "1.0"


def analyze_content(row, assessment):
    """
    AI-assisted qualitative layer.

    The prototype uses deterministic observations so the demonstration
    remains reproducible without requiring an external API key. An approved
    LLM can replace this function later without changing the governance flow.

    Important design boundary: the assessment engine owns the numeric health
    score and preliminary lifecycle recommendation. This layer provides
    qualitative observations only; it does not make the final decision.
    """
    observations = []

    if assessment["freshness"] < 60:
        observations.append("The content appears dated and may require a freshness review.")
    if assessment["quality"] < 70:
        observations.append(
            "Completeness indicators suggest that the page may have missing or outdated metadata/content."
        )
    if assessment["performance"] < 60:
        observations.append(
            "Performance indicators suggest an opportunity to improve the page experience."
        )
    if row["duplicate_similarity"] >= 0.80:
        observations.append(
            "High similarity with other content suggests a possible consolidation opportunity."
        )
    if assessment["engagement"] >= 70:
        observations.append(
            "Engagement evidence suggests the content is actively used and should be considered before retirement."
        )
    if not observations:
        observations.append("Available evidence does not identify a significant governance concern.")

    summary = (
        "The qualitative analysis highlights the evidence-based observations below. "
        "It is advisory and does not determine the final governance decision."
    )
    return {
        "summary": summary,
        "observations": observations,
        "prompt_version": PROMPT_VERSION,
    }
