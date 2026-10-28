# System Architecture and Module Responsibilities

## System Boundary

The current deliverable is a local Streamlit prototype. It reads representative content metadata and analytics-like fields from `data/content_sample.csv`, calculates a deterministic assessment, displays rule-based qualitative observations, and records human review decisions in a local SQLite database.

The prototype does not connect to a production content management system (CMS), live analytics platform, or external large language model (LLM). Its purpose is to demonstrate a structured content-governance workflow while preserving human decision authority.

## Data Flow

1. **Sample evidence** — `data/content_sample.csv` supplies content identifiers, titles, update dates, page views, engagement rate, word count, completeness, duplicate similarity, performance score, content type, and strategic importance.

2. **Assessment engine** — `src/assessment.py` normalizes five indicators, applies configured weights, calculates a rounded 0–100 health score, and produces a preliminary recommendation and rationale.

3. **Qualitative analysis** — `src/ai_analysis.py` applies deterministic threshold rules to the assessment and available evidence. It returns an advisory summary, zero or more observations, a fallback observation if no concerns trigger, and a version label used to identify the analysis configuration. No external model call occurs.

4. **Review interface** — `src/app.py` displays the overview, evidence, assessment, qualitative observations, and human-review controls. The reviewer can record an independent assessment, a final decision, and a required rationale.

5. **Persistence and audit history** — `src/database.py` writes review records to SQLite and retrieves the latest decision for a content item or the complete audit history.

The documented data flow describes the intended responsibilities of each module. Specific behavior should be confirmed against the implementation and its tests.

## Modules

| Module | Responsibility | Key Boundary |
|---|---|---|
| `src/assessment.py` | Indicator scores, weight validation, weighted health score, and preliminary recommendation | Rules are configured design choices, not empirically validated universal measures |
| `src/ai_analysis.py` | Deterministic qualitative observations | Not an external LLM; does not determine the human's final decision |
| `src/app.py` | Streamlit dashboard and human-review workflow | Local prototype; no production CMS write access |
| `src/database.py` | SQLite schema, saved review records, and audit-history retrieval | Local persistence; not production-grade audit security |
| `data/content_sample.csv` | Representative sample records | Intended to contain 24 sample records; not a production inventory |

## Scoring Model

The configured weights are:

| Indicator | Weight |
|---|---:|
| Freshness | 0.20 |
| Quality/completeness | 0.20 |
| Performance | 0.20 |
| Duplication/uniqueness | 0.15 |
| Engagement | 0.25 |
| **Total** | **1.00** |

The weighted scoring formula is:

`H = 0.20F + 0.20Q + 0.20P + 0.15D + 0.25E`

Where:

- `H` represents the overall content-health score.
- `F` represents the normalized freshness score.
- `Q` represents the normalized quality/completeness score.
- `P` represents the normalized performance score.
- `D` represents the normalized duplication/uniqueness score.
- `E` represents the normalized engagement score.

Each component is normalized to a scale of 0–100. The calculated weighted score is rounded to an integer.

The weights are prototype configuration choices and have not been validated against expert judgments or measured business outcomes. The resulting score supports prioritization but does not independently determine whether content should be retained, updated, consolidated, or retired.

## Contextual Recommendation Logic

The current preliminary recommendation rules are documented in the following order:

1. Duplicate similarity at or above `0.80` recommends `Consolidate`.
2. Strategically critical `About` or `Organizational` content with a freshness score below `40` recommends `Review`.
3. Freshness below `40` or quality below `60` recommends `Update`.
4. Overall health below `60` recommends `Review`.
5. Otherwise, recommend `Keep`.

These recommendations are advisory. The interface does not execute content lifecycle changes.

The high-duplication rule precedes the strategic-evergreen rule. If both conditions apply, `Consolidate` takes precedence under this rule order. The strategic-evergreen safeguard is intended to prevent content age alone from automatically triggering an update recommendation for strategically important organizational content.

Any change to recommendation thresholds or rule precedence should be documented and tested. The actual implementation must be checked to confirm that its logic matches this description.

## Persistence and Audit History

The SQLite `audit_log` table is intended to store the content ID, system recommendation, qualitative summary, independent human assessment, final decision, rationale, criteria version, prompt or analysis version, and timestamp.

Saving a new decision should add a new record rather than overwrite earlier decisions, allowing the application to retrieve decision history for a content item.

SQL parameters should be used for content values to reduce SQL injection risk.

The audit log is a local prototype mechanism. It does not, by itself, establish production-grade audit integrity, access control, data retention, or regulatory compliance. The exact schema and persistence behavior should be verified against `src/database.py` and the database tests.

## Security and Governance Boundaries

The prototype uses representative data and local persistence. It does not implement production authentication, authorization, live CMS write access, or an external LLM integration.

Human reviewers retain responsibility for final governance decisions. System recommendations should be interpreted alongside the underlying evidence, content purpose, strategic importance, and organizational requirements.

The deterministic analysis and configured scoring rules should be reviewed before being used to support operational decisions. They are not independently validated measures of content value or organizational impact.

## Deployment and Future Work

Potential future enhancements include:

- Validated CMS and analytics integrations.
- An optional external LLM integration subject to privacy, security, validation, and governance review.
- Stronger input validation and error handling.
- Authentication and authorization.
- Secure secret management and protected audit storage.
- Backup and recovery procedures.
- Accessibility evaluation.
- Concurrency and performance testing.
- Automated deployment and release controls.
- Production monitoring and operational support.

These capabilities are future work and are not represented as implemented in the current prototype.

## Verification and Maintenance

Architecture documentation should remain aligned with the source code, requirements, and automated tests.

Changes to scoring weights, thresholds, recommendation precedence, qualitative-analysis behavior, or database fields should be reflected in the relevant documentation and tests. The complete test suite should be run after implementation changes, and test counts and coverage should be reported only from the actual results of that run.