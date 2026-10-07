import sys
from pathlib import Path

import pandas as pd

sys.path.append("src")

import database


def test_save_and_retrieve_latest_review(tmp_path, monkeypatch):
    test_db = tmp_path / "governance.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)

    database.init_db()
    database.save_review(
        content_id="TEST-001",
        system_recommendation="Update",
        ai_summary="Qualitative observations",
        human_assessment="Keep",
        final_decision="Review",
        rationale="Strategic value warrants additional review.",
    )

    result = database.get_latest_review("TEST-001")

    assert result is not None
    assert result["content_id"] == "TEST-001"
    assert result["system_recommendation"] == "Update"
    assert result["human_assessment"] == "Keep"
    assert result["final_decision"] == "Review"
    assert result["rationale"] == "Strategic value warrants additional review."


def test_latest_review_is_most_recent(tmp_path, monkeypatch):
    test_db = tmp_path / "governance.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)

    database.init_db()
    database.save_review("TEST-002", "Update", "First", "Keep", "Review", "First rationale")
    database.save_review("TEST-002", "Update", "Second", "Review", "Update", "Second rationale")

    result = database.get_latest_review("TEST-002")

    assert result["human_assessment"] == "Review"
    assert result["final_decision"] == "Update"
    assert result["rationale"] == "Second rationale"

def test_get_latest_review_returns_none_when_no_review_exists(tmp_path, monkeypatch):
    test_db = tmp_path / "governance.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)

    database.init_db()

    result = database.get_latest_review("DOES-NOT-EXIST")

    assert result is None


def test_get_audit_records_returns_saved_records(tmp_path, monkeypatch):
    test_db = tmp_path / "governance.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)

    database.init_db()

    database.save_review(
        content_id="TEST-003",
        system_recommendation="Review",
        ai_summary="Audit record test",
        human_assessment="Review",
        final_decision="Review",
        rationale="Testing audit record retrieval.",
    )

    database.save_review(
        content_id="TEST-004",
        system_recommendation="Keep",
        ai_summary="Second audit record",
        human_assessment="Keep",
        final_decision="Keep",
        rationale="Testing multiple audit records.",
    )

    result = database.get_audit_records()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert set(result["content_id"]) == {"TEST-003", "TEST-004"}