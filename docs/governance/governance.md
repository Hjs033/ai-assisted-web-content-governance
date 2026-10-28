# Governance Rules, Human Oversight, and Limitations

## Decision Authority

The system provides evidence and preliminary recommendations to support content governance. A human reviewer remains responsible for the final decision. The prototype does not automatically publish, update, consolidate, or retire content.

The review interface is designed to separate an independent human assessment from the final decision and require a rationale before saving. The SQLite record is intended to retain the system recommendation, qualitative summary, human assessment, final decision, rationale, criteria version, analysis version, and timestamp.

These governance controls are intended to support accountability and traceability. Their exact behavior depends on the implementation and must be verified against the application code and tests.

## Assessment Indicators

The content-health score combines five normalized indicators:

- **Freshness:** Days since the recorded update date, mapped to a normalized score.
- **Quality/completeness:** Completeness value supplied in the dataset.
- **Performance:** Normalized performance score supplied in the dataset.
- **Duplication/uniqueness:** A score derived from duplicate similarity, with higher similarity representing lower uniqueness.
- **Engagement:** Engagement rate scaled to a 0–100 score.

The configured weights are:

| Indicator | Weight |
|---|---:|
| Freshness | 0.20 |
| Quality/completeness | 0.20 |
| Performance | 0.20 |
| Duplication/uniqueness | 0.15 |
| Engagement | 0.25 |
| **Total** | **1.00** |

These weights are prototype configuration choices, not empirically validated measures of universal content quality. The combined score supports prioritization but should not be treated as a definitive measure of content value or organizational importance.

## Contextual Safeguard for Strategic Evergreen Content

The intended recommendation logic identifies content whose type is `About` or `Organizational` and whose strategic importance is `Critical`. If its freshness score is below 40, the rule recommends human review rather than an update recommendation based solely on age.

This safeguard does not guarantee that content is accurate or current. It prevents low freshness alone from being treated as sufficient grounds for an automatic lifecycle action. High duplicate similarity is also a signal for investigation, not proof that a page is redundant or safe to remove.

**Rule precedence matters:** The documented rule order places the high-duplication rule before the strategic-evergreen safeguard. Therefore, content meeting both conditions can receive a `Consolidate` recommendation. This precedence should be reviewed before extending the rule set, and changes should be supported by appropriate tests.

## Qualitative-Analysis Boundary

The `src/ai_analysis.py` module applies deterministic rules to assessment outputs and available content evidence. It produces advisory qualitative observations and a version label identifying the analysis configuration.

The evaluated prototype does not call an external LLM, does not generate the health score through a language model, and does not determine the human's final governance decision.

The project title describes the broader direction of the work; it does not imply that an external generative-AI integration is implemented in the evaluated prototype.

## Data, Privacy, and Security

The 24 records in `data/content_sample.csv` are representative sample data, not a verified production inventory.

Before using real organizational data, the organization should confirm authorization, minimize collected data, establish appropriate access controls, and review any proposed transmission to external services. The current qualitative-analysis module does not call an external service.

The SQLite database provides local persistence and is intended to be excluded from Git. Parameterized SQL should be used for content values to reduce SQL injection risk.

These measures do not constitute a complete security program. Authentication, authorization, protected audit storage, backup and recovery, data-retention policy, and production security testing remain future work.

## Known Limitations and Future Validation

Before production use, the project would require additional validation and operational controls, including:

- Formal user-acceptance and usability testing.
- Accessibility evaluation.
- Security and privacy review.
- Testing of missing, malformed, and boundary inputs.
- Concurrency and database recovery testing.
- Performance testing against a defined, larger content inventory.
- Validated CMS and analytics integrations.
- Integration and security testing before any external LLM is introduced.
- Review of recommendation accuracy with qualified content-governance reviewers.

The system should be treated as a decision-support prototype until the necessary controls and validations are completed.

## Governance Maintenance

Changes to scoring weights, thresholds, recommendation rules, strategic-evergreen handling, or rule precedence should be documented and tested.

Governance documentation should remain aligned with the source code, requirements, and automated tests. Any future external LLM integration should undergo a separate privacy, security, quality, and governance review before use with organizational content.