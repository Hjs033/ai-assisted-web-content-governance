# Requirements and Implementation Traceability

This document records the current implementation status. “Implemented” means a corresponding feature exists in the local prototype; it does not automatically mean that the feature is production-ready or fully validated.

## Functional requirements

| ID | Requirement | Implementation | Current evidence / validation boundary |
|---|---|---|---|
| FR-01 | Load and present content evidence for review | `src/app.py`; `data/content_sample.csv` | Dashboard and record-level evidence are implemented; sample data only |
| FR-02 | Calculate a normalized weighted content-health score | `src/assessment.py` | Assessment unit tests; weights total 1.00; empirical validity not established |
| FR-03 | Produce preliminary lifecycle recommendations using configured rules | `src/assessment.py` | Unit tests cover selected duplicate, freshness, quality, health, and strategic-evergreen scenarios; rule precedence should remain documented |
| FR-04 | Produce qualitative observations that are separate from the numeric score | `src/ai_analysis.py` | Deterministic threshold tests; no external LLM call |
| FR-05 | Preserve human authority over the final governance decision | `src/app.py` | Review controls and required rationale are implemented; no formal multi-user acceptance study |
| FR-06 | Save reviewer assessment, final decision, rationale, and versions | `src/app.py`; `src/database.py` | Database tests cover save/retrieve and latest-record behavior; local SQLite only |
| FR-07 | Retrieve review history | `src/database.py`; `src/app.py` | Database retrieval tests and application empty-history test; no production audit-security validation |
| FR-08 | Protect strategically critical evergreen content from age-only automatic action | `src/assessment.py` | A unit test confirms a critical `About` page with low freshness recommends Review; this is a recommendation rule, not an automated retirement workflow |

## Non-functional requirements and current status

| Area | Current design/implementation | Validation still needed |
|---|---|---|
| Maintainability | Separate assessment, analysis, UI, and database modules; repository version control | Review module boundaries and run regression tests after changes |
| Reproducibility | Deterministic scoring and qualitative rules; criteria/prompt version fields | Confirm version identifiers remain synchronized when configuration changes |
| Usability | Streamlit interface with assessment, human-review, and audit-history tabs | Formal user acceptance, usability testing, and task-based evaluation |
| Reliability | SQLite persistence and automated tests for selected paths | Malformed/missing input cases, backup/recovery, concurrency, and failure handling |
| Security/privacy | Local prototype, parameterized SQL, ignored local database and environment files | Authentication, authorization, secret management, encryption decisions, security review, and deployment testing |
| Accessibility | Not formally evaluated | Keyboard navigation, labels, contrast, screen-reader support, and accessibility testing |
| Performance/scalability | Representative 24-record dataset | Repeatable benchmarks with larger datasets and explicit response-time criteria |
| Integration | CSV input and local SQLite | CMS/analytics adapters and any external LLM integration are future work |

## Test evidence and traceability

The repository contains:

- `tests/test_assessment.py`
- `tests/test_ai_analysis.py`
- `tests/test_app.py`
- `tests/test_database.py`

Run `python -m pytest -q` from the repository root after installing `requirements.txt`. Use the result from the actual final run in any report. Do not treat statement coverage as proof of branch completeness or production readiness.

The final technical report and assignment-specific AB report are separate deliverables; keep their reported results synchronized with the same verified test run. Update this table when requirements, code, tests, or validation status changes.
